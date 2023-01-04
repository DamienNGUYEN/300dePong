# Import required library
import turtle
from client import Client
import ast

try:
    #On se connecte au serveur précisé dans le fichier ipServ.txt
    ipServ = open("ipServ.txt", 'r')
    ip = ipServ.readline()
    
    #On vérifie que l'ip est au bon format
    checkIp = ip.split('.')
    print(ip)
    print(checkIp)
    if len(checkIp) != 4: #Si l'ip ne contient pas 4 nombres, on souleve une erreur
        raise Exception
    for number in checkIp: #Si l'ip ne contient pas que des chiffres, on souleve une erreur
        for i in number:
            if not(i >= '0' and i <= '9'):
                raise Exception
    #Si l'ip est au bon format mais que la cible ne répond pas, le jeu s'arrête
    client = Client(ip, 1234, 1234)
    
except: #Si l'ip ne fonctionne pas, on se connecte au localhost
    client = Client("127.0.0.1", 1234, 1234)

# Create screen
sc = turtle.Screen()
sc.title("300 de Pong")
sc.bgcolor("black")
sc.setup(width=1000, height=600)
sc.cv._rootwindow.resizable(False, False)

# Left paddle
left_pad = turtle.Turtle()
left_pad.speed(0)
left_pad.shape("square")
left_pad.color("white")
left_pad.shapesize(stretch_wid=6, stretch_len=1)
left_pad.penup()
left_pad.goto(-400, 0)
 
 
# Right paddle
right_pad = turtle.Turtle()
right_pad.speed(0)
right_pad.shape("square")
right_pad.color("white")
right_pad.shapesize(stretch_wid=6, stretch_len=1)
right_pad.penup()
right_pad.goto(400, 0)

# Ball of circle shape
hit_ball = turtle.Turtle()
hit_ball.speed(40)
hit_ball.shape("circle")
hit_ball.color("white")
hit_ball.penup()
hit_ball.goto(0, 0)
hit_ball.dx = 8
hit_ball.dy = -5

# Initialize the score
left_player = 0
right_player = 0
localLeftPlayer = 0
localRightPlayer = 0


# Displays the score
sketch = turtle.Turtle()
sketch.speed(0)
sketch.color("white")
sketch.penup()
sketch.hideturtle()
sketch.goto(0, 260)
sketch.write("Waiting for another player...",
             align="center", font=("Courier", 24, "normal"))

# Functions to move paddle vertically
def paddleaup():
    y = left_pad.ycor()
    if y <= 230:
        y += 20
        left_pad.sety(y)
 
 
def paddleadown():
    y = left_pad.ycor()
    if y >= -230:
        y -= 20
        left_pad.sety(y)
    
def leaveRoom():
    client.leave_room()

try:
    client.autojoin()
except:
    client.isHost = True
    client.create_room()
    
#Tant qu'on n'a pas d'adversaire, on attend
client.send("Ping")

while len(client.get_messages()) == 0:
    sc.update()
    
#Préparation de la partie
sketch.clear()
sketch.write("Left_player : 0    Right_player: 0",
             align="center", font=("Courier", 24, "normal"))

noMessageCounter = 0 #Compte le nombre de fois d'affilée que l'adversaire n'a pas
                     #envoye de message. Permet de determiner la deconnexion
    
# Keyboard bindings
#Le joueur peut bouger son pad une fois la partie commencee
sc.listen()
sc.onkeypress(paddleaup, "z")
sc.onkeypress(paddleadown, "s")
sc.onkeypress(leaveRoom, "q")

#La partie commence
while True:
    sc.update()
    
    #Déplacement de la balle
    if client.isHost:
        hit_ball.setx(hit_ball.xcor()+hit_ball.dx)
        hit_ball.sety(hit_ball.ycor()+hit_ball.dy)
    
    #On crée le paquet de données à envoyer
    #data = {"hitBall_X": hit_ball.xcor(), "hitBall_Y": hit_ball.ycor(), "leftPad_Y": left_pad.ycor()}
    if client.isHost:
        data = [left_pad.ycor(), hit_ball.xcor(), hit_ball.ycor(), localLeftPlayer, localRightPlayer]
    else:
        data = [left_pad.ycor()]
    
    #Envoie du paquet au joueur adverse
    client.send(data)
 
    #Lecture des données envoyées par le joueur adverse
    messages = client.get_messages()
    if len(messages) != 0:
        noMessageCounter = 0 #Un message a ete recu, on remet le cpt a 0
        
        for i in messages:
            messageInBytes = i
        dico = messageInBytes.decode("utf-8")
        dico = ast.literal_eval(dico)
        
        try:
            right_pad.sety(dico.get("data")[0])
            if not client.isHost:
                hit_ball.setx(-dico.get("data")[1])
                hit_ball.sety(dico.get("data")[2])
                left_player = dico.get("data")[3]
                right_player = dico.get("data")[4]
        except:
            continue
    else:
        noMessageCounter += 1
        if noMessageCounter >= 100: #Aucun message depuis trop longtemps
            break                   #On arrete le jeu
 
    # Checking borders
    if hit_ball.ycor() > 280:
        hit_ball.sety(280)
        hit_ball.dy *= -1
 
    if hit_ball.ycor() < -280:
        hit_ball.sety(-280)
        hit_ball.dy *= -1
 
    #Si le joueur est hote, il met a jour les scores
    if client.isHost:
        if hit_ball.xcor() > 500:
            hit_ball.goto(0, 0)
            hit_ball.dx = -8 #La balle reprend sa vitesse initiale et part vers le cote gagnant
            localLeftPlayer += 1
            sketch.clear()
            sketch.write("Left_player : {}    Right_player: {}".format(
                          localLeftPlayer, localRightPlayer), align="center",
                          font=("Courier", 24, "normal"))
     
        if hit_ball.xcor() < -500:
            hit_ball.goto(0, 0)
            hit_ball.dx = 8 #La balle reprend sa vitesse initiale et part vers le cote gagnant
            localRightPlayer += 1
            sketch.clear()
            sketch.write("Left_player : {}    Right_player: {}".format(
                                     localLeftPlayer, localRightPlayer), align="center",
                                     font=("Courier", 24, "normal"))

    #Sinon, il recupere ceux envoyes par l'adversaire
    else:
        if localLeftPlayer != right_player or localRightPlayer != left_player:
            sketch.clear()
            sketch.write("Left_player : {}    Right_player: {}".format(
                                     right_player, left_player), align="center",
                                     font=("Courier", 24, "normal"))
            localLeftPlayer = right_player
            localRightPlayer = left_player
            
    if localLeftPlayer >= 5 or localRightPlayer >= 5:
        
        #Envoi du score final a l'adversaire
        #data = {"hitBall_X": hit_ball.xcor(), "hitBall_Y": hit_ball.ycor(), "leftPad_Y": left_pad.ycor()}
        if client.isHost:
            data = [left_pad.ycor(), hit_ball.xcor(), hit_ball.ycor(), localLeftPlayer, localRightPlayer]
        else:
            data = [left_pad.ycor()]
        
        #Envoie du paquet au joueur adverse
        client.send(data)
        
        break
        
    #Collision de la balle et des pads, uniquement pour l'hote
    if client.isHost:
        if (hit_ball.xcor() > 360 and hit_ball.xcor() < 390) and (hit_ball.ycor() < right_pad.ycor()+80 and hit_ball.ycor() > right_pad.ycor()-100):
            hit_ball.setx(360)
            hit_ball.dx += 2 #En touchant le pad, la balle accelere un peu
            hit_ball.dx *= -1 #Et la balle part dans le sens oppose
            
        if (hit_ball.xcor()<-360 and hit_ball.xcor()>-390) and (hit_ball.ycor()<left_pad.ycor()+80 and hit_ball.ycor()>left_pad.ycor()-100):
            hit_ball.setx(-360)
            hit_ball.dx -= 2 #Le sens est opposé, d'où la soustraction
            hit_ball.dx *= -1
        
        
#Une fois que le joueur adverse est deconnecte
sketch.clear()

if localLeftPlayer >= 5:
    sketch.write("Victory !", 
                 align="center", font=("Courier", 24, "normal"))
    
elif localRightPlayer >= 5:
    sketch.write("Defeat !", 
                 align="center", font=("Courier", 24, "normal"))
else:       
    sketch.write("Won by forfait !", 
             align="center", font=("Courier", 24, "normal"))
while True:
    sc.update()