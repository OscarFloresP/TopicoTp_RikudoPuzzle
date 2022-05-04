# Add image file
from tkinter import *
from tkinter import messagebox
from PIL import Image,ImageTk
import rikudo
import random


class RikudoPuzzle:
    def __init__(self):
        self.__start_tk__()
        self.__start_main_menu__()

    def __start_tk__(self):
        self.root = Tk()
        self.root.resizable(width=False, height=False) # Lock window size
        self.root.geometry("620x600") # Set size
        self.img_bg = ImageTk.PhotoImage((Image.open("mapa.png")).resize((620, 600), Image.ANTIALIAS)) # Load image and resize

        self.background_label = Label(self.root, image=self.img_bg)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def __start_main_menu__(self):
        self.rt = rikudo.Table()
        self.nodes_and_pixels = self.rt.get_nodes_and_pixels(50)
        
        self.botonRandom = Button(text = "RANDOM\nSAMPLE",command = self.generate_random)
        self.botonCustom = Button(text = "CONFIGURE\nSAMPLE",command = self.__configure__phase1__)

        self.text_boxs = {}
        for k, v in self.nodes_and_pixels.items():
            Tvar = StringVar()
            T = Entry(self.root, textvariable=Tvar, width = 5)
            T.place(x=v[0] - 100, y=v[1] + 60)
            self.text_boxs[k] = [T, Tvar]

        self.__switch_text_box__("disabled")

        self.botonRandom.place(x=20,y=440)
        self.botonCustom.place(x=20,y=500)

    def __restart_rikudo_puzzle__(self):
        self.root.destroy()
        self.__start_tk__()
        self.__start_main_menu__()

    def __switch_text_box__(self, state:str):
        color = "#B9B9B9" if state=="disabled" else "#FFFFFF"
        color = "Lightgrey" if state=="disabled" else "White"
        [vobj.configure({"background": color}, state=state) for k, (vobj, vvar) in self.text_boxs.items()]

    def __configure__phase1__(self):
        # Check function INI
        def check_function():
            result = [(k, vvar.get()) for k, (vobj, vvar) in self.text_boxs.items()]
            
            try:
                result = [(k, int(v)) for k, v in result if v != ""]
                if len(result) != len(list(set([v for _, v in result]))): # different numbers
                    messagebox.showinfo("Error","Error: integers must be diferent")
                    # print("Error: integers must be diferent")
                elif sum([(v < 1 or 36 < v) for k, v in result]):
                    messagebox.showinfo("Error","Error: input must be between 1 and 36")
                    # print("Error: input must be between 1 and 36")
                else:
                    self.ltuples, self.lvalues = [], []
                    if len(result) != 0:
                        self.ltuples, self.lvalues = tuple(zip(*result))
                    self.botonNext.destroy()
                    self.__switch_text_box__("disabled")
                    self.__configure__phase2__()
            except:
                messagebox.showinfo("Error","Error: input must be integers")
                # print("Error: input must be integers")
        self.botonRandom.place_forget()
        self.botonCustom.place_forget()
        # Check function END

        self.__switch_text_box__("normal")
        self.botonNext = Button(text = "NEXT",command = check_function)
        self.botonNext.place(x=540,y=440)
        # Boton Back To Main Menu
        self.botonBTMM = Button(text = "RETURN\nMAIN MENU\n(RESTART)",command = self.__restart_rikudo_puzzle__)
        self.botonBTMM.place(x=520,y=500)


    def __configure__phase2__(self):
        # Check function INI
        def check_function():
            result = [(k, vvar.get()) for k, (vobj, vvar) in self.check_boxs.items()]
            result = [k for k, v in result if v != 0] ## Verify which ones are selected

            # Destroy only the ones are not selected
            no_result = [k for k in self.check_boxs.keys() if k not in result]
            [self.check_boxs[k][0].destroy() for k in no_result]

            self.botonNext.destroy()
            # Solve Button
            self.botonSolve = Button(text = "SOLVE\nRIKUDO",command = self.solve_puzzle)
            self.botonSolve.place(x=540,y=440)

            self.lpairs = result
        # Check function END

        self.check_boxs= {}
        for ax_i, ax_j in self.rt.get_neighbors():
            Cvar = IntVar()
            C = Checkbutton(self.root, variable=Cvar, onvalue=1, offvalue=0, bg="#A4D176")
            pfinal = [(a+b)/2 for a, b in zip(self.nodes_and_pixels[ax_i], self.nodes_and_pixels[ax_j])]
            C.place(x=pfinal[0] - 90, y=pfinal[1] + 60)
            self.check_boxs[(ax_i), (ax_j)] = [C, Cvar]

        self.botonNext = Button(text = "NEXT",command = check_function)
        self.botonNext.place(x=540,y=440)

    def generate_random(self, rmin=9, rmax=12):
        nodes = self.rt.generate(random.randint(1, 36))
        nodes = random.choices([(k, v) for k, v in nodes.items() ], k=random.randint(rmin, rmax) )
        
        [ self.text_boxs[k][1].set(str(v)) for k, v in nodes ]

        # Boton Back To Main Menu
        self.botonBTMM = Button(text = "RETURN\nMAIN MENU\n(RESTART)",command = self.__restart_rikudo_puzzle__)
        self.botonBTMM.place(x=520,y=500)


    def solve_puzzle(self):
        self.botonSolve.place_forget()
        
        print(self.ltuples, self.lvalues, self.lpairs)
        nodes = self.rt.solve(self.ltuples, self.lvalues, self.lpairs)
        if nodes == None:
            # print("No solution found")
            messagebox.showinfo("Error","Error: No solution found")
            return
        [ self.text_boxs[k][1].set(str(v)) for k, v in nodes.items() ]

if __name__ == "__main__":
    
    rp = RikudoPuzzle()

    rp.root.mainloop()