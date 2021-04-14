import tkinter as tk
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename
import generate_passages


def get_books():
    books = []
    for filename in os.listdir("data/books/"):
        with open("data/books/" + filename, 'r') as f:
            title = f.readline().strip().split(' ')
            instance = [filename] + title[4:]
            print(instance)
            if instance[1] == 'of':
                instance.pop(1)
            print(instance)
            books.append(' '.join(instance))
            
        
    return books


def main():
    window = tk.Tk()
    window.title("Annotater")
    window.rowconfigure(0, minsize=50, weight=1)
    window.columnconfigure(0, minsize=300, weight=1)
    window.columnconfigure(1, minsize=300, weight=1)

    # main windows 
    txt_book = tk.Text(window, state='disabled', width=44)
    txt_edit = tk.Text(window)
    select_names = tk.Frame(window)
    data_selection = tk.Frame(window, relief=tk.RAISED, bd=2)
    fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

    def book_select_callback(*args):
        book_select.get()

    def open_file():
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        txt_edit.delete(1.0, tk.END)
        with open(filepath, "r") as input_file:
            text = input_file.read()
            txt_edit.insert(tk.END, text)

        window.title(f"Annotating - {filepath}")

    def save_file():
        """Save the current file as a new file."""
        filepath = asksaveasfilename(
            defaultextension="txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        with open(filepath, "w") as output_file:
            text = txt_edit.get(1.0, tk.END)
            output_file.write(text)
        window.title(f"Simple Text Editor - {filepath}")

    def start_annotation():
        if book_select.get() != "":
            book_filename = book_select.get().split(" ")[0]
            book_title = book_select.get().split(" ")
            book_title = ' '.join(book_title[1:book_title.index('by')])[:-1]
            print("\nStart annotating")
            print("book_title:",book_title)
            print("book_filename:", book_filename)

        if name1.get() != "" and name2.get() != "":
            print("Name1: ", name1.get())
            print("Name2: ", name2.get())


    books = ["one","two","three"]

    book_select = tk.StringVar(data_selection)
    book_filename = ""
    book_select.set("select book")
    book_select.trace("w", book_select_callback)
    book_dropdown = tk.OptionMenu(data_selection, book_select, *get_books())
    book_dropdown.configure(width=30)

    label_name1 = tk.Label(select_names, text="Enter name 1: ")
    name1 = tk.Entry(select_names)
    label_name2 = tk.Label(select_names, text="Enter name 2: ")
    name2 = tk.Entry(select_names)


    btn_start = tk.Button(select_names, text="Go", width=4, height=3, command=start_annotation)

    btn_next = tk.Button(fr_buttons, text="next")
    btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)


    label_name1.grid(row=0, column=0)
    name1.grid(row=0, column=1)
    label_name2.grid(row=1, column=0)
    name2.grid(row=1, column=1)
    btn_start.grid(row=0, column=2, rowspan=2, sticky="ew")

    

    book_dropdown.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    btn_next.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    btn_save.grid(row=2, column=1, sticky="ew", padx=5)

    data_selection.grid(row=0, column=0, sticky="ns")
    select_names.grid(row=0, column=1, sticky="nsew")

    fr_buttons.grid(row=1, column=0, sticky="ns")
    txt_book.grid(row=1, column=1, sticky="nsew")
    txt_edit.grid(row=2, column=1, sticky="nsew")


    window.mainloop()

if __name__ == "__main__":
    main()