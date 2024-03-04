import string
import os
import psutil
import json
import re
import pyAesCrypt
import customtkinter as ctk
from threading import Thread
from tkinter import messagebox

COUNTFILES = '--'

class BackEnd:

    bufferSize = 256 * 1024

    @staticmethod
    def count_files():
        global COUNTFILES
        FC = 0
        for root, dirs, files in os.walk(CURRENT_DRIVE + ':/'):
                for file_name in files:
                    FC = FC + 1
                    COUNTFILES = str(FC)
        COUNTFILES = str(int(COUNTFILES) - 1)


    @staticmethod
    def encrypt_file(path, password):
        if not path.endswith('usbsecure.json'):
            pyAesCrypt.encryptFile(path, path+'.usbsecure', password, BackEnd.bufferSize)
            os.remove(path)
        
    
    def decrypt_file(path, password):
        if not path.endswith('usbsecure.json'):
            pyAesCrypt.decryptFile(path, path.replace('.usbsecure', ''), password, BackEnd.bufferSize)
            os.remove(path)

    @staticmethod
    def get_drive_filesystem(letter):
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if partition.device.startswith(letter):
                    return partition.fstype
        except Exception as e:
            return 'Unknown'
        return 'Unknown'

    @staticmethod
    def get_devices_list():
        disks = []
        alphabet_upper = list(string.ascii_uppercase)
        for letter in alphabet_upper:
            if os.path.exists(f'{letter}:/'):
                disks.append(letter)
        print('All drives: ' + str(disks))
        return disks

    @staticmethod
    def is_disk_crypted(letter):
        if os.path.exists(f'{letter}:/usbsecure.json'):
            try:
                with open(f'{letter}:/usbsecure.json', 'r') as file:
                    data = json.load(file)
                    if data['isencrypted'] == 'True':
                        return True
            except Exception as openerr:
                return None
        else:
            return False



class MainWindow:

    @staticmethod
    def main():

        def validate_password(password):
            if len(password) < 8:
                return False
            else:
                return True

        def main_action():
            password = password_input.get()
            if password == '' or validate_password(password) == False:
                return messagebox.showerror(title='Password error', message="Invalid password, must be > 7 symbols")
            else:
                answer = messagebox.askquestion(title='Are you sure?', message="All data will be encrypted / decrypted, are you sure?")
                if answer == 'no':
                    return
            
            
            if BackEnd.is_disk_crypted(CURRENT_DRIVE) == True:
                ACTION='dec'
            else:
                ACTION='enc'
            
            county = ctk.CTkLabel(logs_frame, text="")
            county.pack()
            COUNTY = 0
            Thread(target=BackEnd.count_files).start()

            action_button.configure(state='disabled')
            password_input.configure(state='disabled')
            fix_button.configure(state='disabled')

            for root, dirs, files in os.walk(CURRENT_DRIVE + ':/'):
                for file_name in files:
                    county.configure(text="Working with file: " + file_name + f'\nTotal: {str(COUNTY)}/{COUNTFILES}')
                    print('Working with file: ' + file_name)
                    try:
                        file_path = os.path.join(root, file_name)
                        COUNTY = COUNTY + 1
                        if ACTION == 'enc':
                            if not file_name == 'usbsecure.json':
                                Thread(target=BackEnd.encrypt_file(file_path, password)).start()
                        else:
                            if not file_name == 'usbsecure.json':
                                Thread(target=BackEnd.decrypt_file(file_path, password)).start()

                    except Exception as exl:
                        exl = str(exl)
                        if exl.startswith('Wrong password'):
                            action_button.configure(state='normal')
                            password_input.configure(state='normal')
                            fix_button.configure(state='normal')
                            return messagebox.showerror(title='Password error', message="Invalid password, can't decrypt")
                        ctk.CTkLabel(logs_frame, text="1 file skipped with reason:\n" + exl).pack()
            
            if ACTION == 'enc':
                is_encrypted_label.configure(text='Is device encrypted: Yes')
                open(f'{CURRENT_DRIVE}:/usbsecure.json', 'w').write('{"isencrypted":"True"}')
            else:
                is_encrypted_label.configure(text='Is device encrypted: No')
                open(f'{CURRENT_DRIVE}:/usbsecure.json', 'w').write('{"isencrypted":"False"}')

            action_button.configure(state='normal')
            password_input.configure(state='normal')
            fix_button.configure(state='normal')
            messagebox.showinfo(title="All done", message=f"All done.\nTotal: {str(COUNTY)}")

            
        def fix_dual_names():
            action_button.configure(state='disabled')
            password_input.configure(state='disabled')
            fix_button.configure(state='disabled')
            fixed_label = ctk.CTkLabel(logs_frame, text="Total fixed: 0")
            skipped_label = ctk.CTkLabel(logs_frame, text="Total skipped: 0")
            fixed_label.pack()
            skipped_label.pack()
            FIXED = 0
            SKIPPED = 0
            for root, dirs, files in os.walk(CURRENT_DRIVE + ':/'):
                for file_name in files:
                    try:
                        file_path = os.path.join(root, file_name)
                        if file_name.endswith('.usbsecure.usbsecure'):
                            normalise = file_path.replace('.usbsecure.usbsecure', '.usbsecure')
                            os.rename(file_path, normalise)
                            FIXED = FIXED + 1
                            fixed_label.configure(text='Total fixed: '+str(FIXED))
                        else:
                            SKIPPED = SKIPPED + 1
                            skipped_label.configure(text='Total skipped: '+str(SKIPPED))
                    except Exception as wtf_err:
                        ctk.CTkLabel(logs_frame, text=str(wtf_err)).pack()
            action_button.configure(state='normal')
            password_input.configure(state='normal')
            fix_button.configure(state='normal')
                            

        def work_with_disk(letter: str):
            global CURRENT_DRIVE
            CURRENT_DRIVE = letter
            is_enc_answer = BackEnd.is_disk_crypted(letter)
            if is_enc_answer == True:
                IS_ENCRYPTED_DRIVE = 'Yes'
            else:
                IS_ENCRYPTED_DRIVE = 'No'
            DRIVE_FILESYSTEM = BackEnd.get_drive_filesystem(letter)
            diskname_label.configure(text='Selected device: ' + letter)
            filesystem_type_label.configure(text='Device filesystem: ' + DRIVE_FILESYSTEM)
            is_encrypted_label.configure(text='Is device encrypted: ' + IS_ENCRYPTED_DRIVE)
            action_button.configure(state='normal')
            password_input.configure(state='normal')
            fix_button.configure(state='normal')
            print('Selected ' + letter + ':/' + ' drive')


        def write_disks_list_gui():
            info_label = ctk.CTkLabel(devices_frame, text="Getting disks info...", fg_color="transparent")
            info_label.pack()
            disklist = BackEnd.get_devices_list()
            info_label.pack_forget()
            for disk in disklist:
                _button = ctk.CTkButton(devices_frame, text=f"Device {disk}:\\", command=lambda disk=disk: Thread(target=work_with_disk, args=(disk,)).start())
                _button.pack()
                ctk.CTkLabel(devices_frame, text="").pack()

        app = ctk.CTk()
        app.geometry("800x500")
        app.title("USB Secure Utility")

        devices_frame = ctk.CTkScrollableFrame(app, width=300, height=475)
        devices_frame.grid(row=0, column=0, padx=5, pady=5)

        logs_frame = ctk.CTkScrollableFrame(app, width=410, height=300)
        logs_frame.place(x=350, y=180)
        ctk.CTkLabel(logs_frame, text="Logs will be here.").pack()

        write_disks_list_gui()

        diskname_label = ctk.CTkLabel(app, text="Selected device: None", font=('', 24))
        diskname_label.place(x=350, y=5)
        password_input_label = ctk.CTkLabel(app, text="Type password to encrypt device:")
        password_input_label.place(x=350, y=40)
        password_input = ctk.CTkEntry(app, placeholder_text="example password")
        password_input.place(x=545, y=40)
        filesystem_type_label = ctk.CTkLabel(app, text="Device filesystem: None")
        filesystem_type_label.place(x=350, y=70)
        is_encrypted_label = ctk.CTkLabel(app, text="Is device encrypted: None")
        is_encrypted_label.place(x=350, y=100)
        action_button = ctk.CTkButton(app, text="Encrypt / Decrypt", command=lambda: Thread(target=main_action).start())
        action_button.place(x=350, y=140)
        fix_button = ctk.CTkButton(app, text="Fix dual names", command=lambda: Thread(target=fix_dual_names).start())
        fix_button.place(x=500, y=140)

        action_button.configure(state='disabled')
        password_input.configure(state='disabled')
        fix_button.configure(state='disabled')

        app.resizable(width=False, height=False)
        app.mainloop()


if __name__ == '__main__':
    MainWindow.main()
