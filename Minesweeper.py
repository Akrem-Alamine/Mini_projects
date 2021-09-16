class User:
        def __init__(self,name,passwd):   #encrypted passwd
            self.name=name
            self.passwd=passwd
            self.games=0 
            self.wins=0
            self.flip_count=0
            self.locked=True
        def update(self,win=False):
            self.games+=1
            self.flip_count=0
            if win:
                self.wins+=1
        def __str__(self):
            return self.name+':'+str(self.games)+'g/'+str(self.wins)+'w'

def login():
    import os.path as op
    if not op.isfile('save.p'):
        import pickle
        pickle.dump({},open('save.p','wb'))
    def verif(name,password='_',info='name',state='old'):
        import pickle
        users=pickle.load(open('save.p','rb'))
        if info=='name':
            if list(users.keys()).count(name)==1:
                if state=='old':
                    return True
                elif state=='new':
                    print('username taken!')
                    return False
            else:
                if state=='old':
                    return False
                elif state=='new':
                    users[name]=User(name,password)
                    pickle.dump(users,open('save.p','wb'))
                    return users[name]
        elif info=='password' and state=="old":
            user=users[name]
            if user.passwd==password:
                user.locked=False
                return True
            else:
                return False
 
    user_mode=input("Play as a guest(g)/user(u)/new user(n)?: ")
    from getpass import getpass
    if user_mode=="u":
        while True:
            name=input("Enter name: ")
            if verif(name,info='name'):
                from getpass import getpass
                password = getpass(f"Enter password for {name} account")
                def rot_13(password):
                    res=''
                    for char in password:
                        res+=chr(ord(char)+13)
                    return res
                if verif(name,password,info='password'):
                    import pickle
                    users=pickle.load(open('save.p','rb'))
                    return users[name]
                break
            else:
                print('Wrong login name!')
    elif user_mode=='n':
        return verif(input("enter name: "),getpass("Enter password: "),state='new')
        
user=login()
print(user)

def play(user):
    assert type(user)==User
    def colored(string,color):
        return f"\x1b[{color}m{string}\x1b[0m"
    from os import system,name
    def clear():            #a function used to clear the screen
        if name=="nt":
            _=system('cls')
        else:
            _=system('clear')
    def verif_coord(x,y,l):
        return (0<=x<=l-1)and(0<=y<=l-1)
    def flip(x,y,user):
        if  verif_coord(x,y,l):
            if surface[x][y][0]=="empty" and surface[x][y][2]=='down':
                surface[x][y][2]="up"
                print(user)
                user.flip_count+=1
                if surface[x][y][1]==0:
                    flip(x-1,y+1,user);flip(x-1,y,user);flip(x-1,y-1,user)
                    flip(x+1,y+1,user);flip(x+1,y,user);flip(x+1,y-1,user)
                    flip(x,y+1,user);flip(x,y-1,user)       
    def update_3d(surface_3d):
        for x in range(l):
            for y in range(l):
                if (surface[x][y][0]!='bomb')and(surface[x][y][2]=='up') and (surface_3d[x][y]=='■'):
                    surface_3d[x][y]=colored(str(surface[x][y][1]),"1;37;40")
    def show_3d(surface_3d):
        clear()
        print('  ',end='')
        for x in range(l):
            print(colored('|'+chr(ord('a')+x),'1;34;40'),end='')
        print(colored('|\n','1;34;40'),end='')
        for x in range(l):
            for y in range(l+1):
                if y==0:
                    print(colored('|'+chr(ord('a')+x),'1;34;40'),end='')
                else:
                    print(colored('|'+surface_3d[x][y-1],'1;36;40'),end='')
            print('|\n',end='')
    def end_game(x,y):
        from playsound import playsound
        playsound('/home/cyberx/Downloads/Game Over sound effect.mp3')
        print('GAME OVER!!!')
    def save_update(user):
        import pickle
        users=pickle.load(open('save.p','rb'))
        users[user.name]=user
        pickle.dump(users,open('save.p','wb'))
    game_over=False;
    while True:
        mode=input("what mode?(e:easy/h:hard)")
        if mode=="e":
            l=8
            bombs=10
            break
        elif mode == "h":
            l=14
            bombs=40
            break
        else:
            print("re-enter mode")
    surface=[ [ ["empty",0,'down'] for y in range(l)] for x in range(l) ] 

    import random as rand;
    for i in range(bombs): #spawn bombs in random coordinates after verifying the coordinates being in the surface
        while True:        #and different from a already spawned bomb
            x=rand.randint(0,l-1);
            y=rand.randint(0,l-1);
            if verif_coord(x,y,l) and surface[x][y][0]=="empty": #update the bomb count for each card in 3*3 matrice
                #{
                surface[x][y]=["bomb"]
                for x_card in range(x-1,x+2):
                    for y_card in range(y-1,y+2):
                        if verif_coord(x_card,y_card,l) and (x_card,y_card)!=(x,y) and (surface[x_card][y_card][0]!="bomb"):
                            surface[x_card][y_card][1]+=1
                #}
                break
    surface_3d=[[[] for y in range(l)] for x in range(l)]
    for x in range(l):
        for y in range(l):   
            surface_3d[x][y]='■'
    while not game_over:
        while True:
            show_3d(surface_3d)
            print("choose an x and y to flip:");
            while True:
                x=ord(input("enter x:"))-ord('a')
                y=ord(input("enter y:"))-ord('a')
                if (0<=x<=l-1) and (0<=y<=l-1):
                    break
            if  verif_coord(x,y,l):
                if surface[x][y][0]=='bomb':
                    end_game(x,y)
                    user.update()
                    save_update(user)
                    if input('replay?(y/n)')=='n':
                        game_over=True
                        break
                    else:
                        play(user)
                elif surface[x][y][2]=="down":
                    flip(x,y,user) #update surface_3d
                    update_3d(surface_3d)
                    show_3d(surface_3d)
                    if user.flip_count==(l*l)-bombs:
                        print('You won!')
                        import time
                        time.sleep(1.2)
                        user.update(win=True)
                        if input('replay?(y/n)')=='n':
                            game_over=True
                            break
                        else:
                            play(user)
                else:
                    print('Card already flipped!')
    
            else:
                print('Coordinates out of board!')
play(user)
#to-do:implement a better way of user input based on a command
#in which the user can tag points,flip and visualize(show the square around n points)
#game over animation(explosion of the board with sleep module)
#win animation(sound)