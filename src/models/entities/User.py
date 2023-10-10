from werkzeug.security import check_password_hash
from flask_login import UserMixin


class User(UserMixin):
    
    def __init__(self,idusuario,usuario,contraseña,nombre="" ) -> None:
        self.id= idusuario
        self.usuario= usuario
        self.contraseña= contraseña
        self.nombre= nombre
    
    @classmethod #para no tener que intanciar las clases, para comprobar la contraseña
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

