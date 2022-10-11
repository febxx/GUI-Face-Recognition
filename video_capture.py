import tkinter as tk
from tkinter import ttk
import json
from urllib.request import urlopen 
import math

with urlopen("https://swapi.dev/api/planets/") as re:
    source = re.read()
planets = json.loads(source)

planet_count = planets['count']
items = [str(n) for n in range(planet_count)]

page = 0
per_page = 10
n_pages = math.ceil((planet_count) / per_page)

def show_table(page): 
    print(page+1)
    count = 0    
    api_url = f"https://swapi.dev/api/planets/?page={str(page+1)}" 
    with urlopen(api_url) as response:
        source_bytecode = response.read()
    planet_data = json.loads(source_bytecode)
    listBox.delete(*listBox.get_children())
    for planet in planet_data['results']:       
        print(planet['name'])
        listBox.insert("", "end", values=(count+1, planet['name'], planet['climate'], planet['diameter'], planet['terrain'], planet['population']))
        count= count+1

main_application = tk.Tk() 
main_application.geometry('1200x800')
main_application.title('Strygwyr')
top_label = tk.Label(main_application, text="LED Swords", font=("Arial",30)).grid(row=0, columnspan=3)
# create Treeview with 6 columns
cols = ('Position', 'Name', 'Climate', 'Diameter', 'Terrain' , 'Population')
listBox = ttk.Treeview(main_application, columns=cols, show='headings')
# set column headings
for col in cols:
    listBox.heading(col, text=col)    
listBox.grid(row=1, column=0, columnspan=2)

# showTable = tk.Button(main_application, text="Populate table", width=15, command=lambda: show_table(page)).grid(row=4, column=0)
closeButton = tk.Button(main_application, text="Close", width=15, command=exit).grid(row=4, column=1)

def change_page(delta):
    global page
    page = min(n_pages - 1, max(0, page + delta))
    update_list()

def update_list():
    print(page+1)
    start_index = int(page * per_page)
    end_index = int((page + 1) * per_page)
    items_in_page = items[start_index:end_index]
    view_text = "Page %d/%d: %s" % (page + 1, n_pages, ", ".join(items_in_page))
    show.delete(0, tk.END)
    show.insert(0, view_text)
    show_table(page)

def prev_btn():
    change_page(-1)

def next_btn():
    change_page(+1)

tk.Button(main_application, text="next", command=next_btn).grid(row=5, column=0)
tk.Button(main_application, text="prev", command=prev_btn).grid(row=5, column=1)

show = tk.Entry(main_application)
show.grid(row= 6, columnspan =3)
update_list() 

main_application.mainloop()