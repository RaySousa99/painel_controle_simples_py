import hashlib
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

ARQUIVO_USUARIOS = 'usuarios.txt'
ARQUIVO_LOGINS = 'logins.txt'
ADMIN_USUARIO = 'admin'
ADMIN_SENHA = '123456'

# Funções de backend
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4)

def registrar_login(usuario):
    logins = {}
    if os.path.exists(ARQUIVO_LOGINS):
        with open(ARQUIVO_LOGINS, 'r') as f:
            try:
                logins = json.load(f)
            except json.JSONDecodeError:
                pass
    logins[usuario] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(ARQUIVO_LOGINS, 'w') as f:
        json.dump(logins, f, indent=4)

def carregar_logins():
    if not os.path.exists(ARQUIVO_LOGINS):
        return {}
    with open(ARQUIVO_LOGINS, 'r') as f:
        return json.load(f)

def deletar_todos():
    if os.path.exists(ARQUIVO_USUARIOS):
        os.remove(ARQUIVO_USUARIOS)
    if os.path.exists(ARQUIVO_LOGINS):
        os.remove(ARQUIVO_LOGINS)

def deletar_usuario_especifico(nome):
    usuarios = carregar_usuarios()
    if nome in usuarios:
        del usuarios[nome]
        salvar_usuarios(usuarios)
        logins = carregar_logins()
        if nome in logins:
            del logins[nome]
            with open(ARQUIVO_LOGINS, 'w') as f:
                json.dump(logins, f, indent=4)

# Interface tkinter
class SistemaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Login")
        self.root.geometry("300x250")
        self.root.configure(bg="#f0f0f0")

        self.usuario_logado = None
        self.montar_tela_login()

        if ADMIN_USUARIO not in carregar_usuarios():
            usuarios = carregar_usuarios()
            usuarios[ADMIN_USUARIO] = {'senha': hash_senha(ADMIN_SENHA)}
            salvar_usuarios(usuarios)

    def montar_tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Login", font=("Helvetica", 16), bg="#f0f0f0").pack(pady=10)
        self.usuario_entry = tk.Entry(self.root)
        self.usuario_entry.pack(pady=5)
        self.senha_entry = tk.Entry(self.root, show="*")
        self.senha_entry.pack(pady=5)
        tk.Button(self.root, text="Entrar", command=self.fazer_login, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Registrar", command=self.tela_registro, bg="#2196F3", fg="white").pack()

    def tela_registro(self):
        top = tk.Toplevel(self.root)
        top.title("Registrar")
        top.geometry("250x180")

        tk.Label(top, text="Usuário:").pack()
        usuario = tk.Entry(top)
        usuario.pack()

        tk.Label(top, text="Senha:").pack()
        senha = tk.Entry(top, show="*")
        senha.pack()

        def registrar():
            nome = usuario.get().strip()
            senha_valor = senha.get().strip()

            if len(nome) < 3 or len(nome) > 20:
                messagebox.showerror("Erro", "Usuário deve ter entre 3 e 20 caracteres.")
                return
            if len(senha_valor) < 4 or len(senha_valor) > 20:
                messagebox.showerror("Erro", "Senha deve ter entre 4 e 20 caracteres.")
                return

            usuarios = carregar_usuarios()
            if nome in usuarios:
                messagebox.showerror("Erro", "Usuário já existe.")
                return
            usuarios[nome] = {'senha': hash_senha(senha_valor)}
            salvar_usuarios(usuarios)
            messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
            top.destroy()

        tk.Button(top, text="Registrar", command=registrar, bg="#4CAF50", fg="white").pack(pady=10)

    def fazer_login(self):
        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get().strip()

        usuarios = carregar_usuarios()
        if usuario in usuarios and usuarios[usuario]['senha'] == hash_senha(senha):
            self.usuario_logado = usuario
            registrar_login(usuario)
            self.montar_tela_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def montar_tela_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Bem-vindo, {self.usuario_logado}!", font=("Helvetica", 14), bg="#f0f0f0").pack(pady=10)

        if self.usuario_logado == ADMIN_USUARIO:
            tk.Button(self.root, text="Listar Usuários", command=self.listar_usuarios, bg="#2196F3", fg="white").pack(pady=5)
            tk.Button(self.root, text="Deletar Todos", command=self.deletar_todos_admin, bg="#f44336", fg="white").pack(pady=5)
            tk.Button(self.root, text="Deletar Específico", command=self.deletar_usuario_popup, bg="#FFC107").pack(pady=5)

        tk.Button(self.root, text="Ver Atividades", command=self.ver_atividades, bg="#9C27B0", fg="white").pack(pady=5)
        tk.Button(self.root, text="Sair", command=self.logout, bg="#607D8B", fg="white").pack(pady=10)

    def logout(self):
        self.usuario_logado = None
        self.montar_tela_login()

    def listar_usuarios(self):
        usuarios = carregar_usuarios()
        logins = carregar_logins()
        texto = "Usuários cadastrados:\n"
        for u in usuarios:
            ultima = logins.get(u, "Nunca")
            texto += f"- {u} | Última atividade: {ultima}\n"
        messagebox.showinfo("Usuários", texto)

    def ver_atividades(self):
        logins = carregar_logins()
        if self.usuario_logado in logins:
            msg = f"Último login: {logins[self.usuario_logado]}"
        else:
            msg = "Este é seu primeiro login."
        messagebox.showinfo("Atividades", msg)

    def deletar_todos_admin(self):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar todos os dados?"):
            deletar_todos()
            messagebox.showinfo("Sucesso", "Todos os dados foram deletados.")
            self.logout()

    def deletar_usuario_popup(self):
        top = tk.Toplevel(self.root)
        top.title("Deletar Usuário")
        top.geometry("250x100")

        tk.Label(top, text="Selecione um usuário:").pack(pady=5)
        usuarios = [u for u in carregar_usuarios() if u != ADMIN_USUARIO]
        combo = ttk.Combobox(top, values=usuarios)
        combo.pack(pady=5)

        def deletar():
            nome = combo.get()
            if nome:
                deletar_usuario_especifico(nome)
                messagebox.showinfo("Sucesso", f"Usuário '{nome}' deletado.")
                top.destroy()

        tk.Button(top, text="Deletar", command=deletar, bg="#f44336", fg="white").pack(pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    app = SistemaLogin(root)
    root.mainloop()
