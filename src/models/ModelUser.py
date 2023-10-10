from .entities.User import User


class ModelUser():
    
    @classmethod
    def login(self, db, user):
        try:
            cursor= db.connection.cursor()
            sql="""SELECT  idusuario, usuario, contraseña FROM login
                    WHERE usuario = '{}'""".format(user.usuario)
            cursor.execute(sql,)
            row = cursor.fetchone()
            print(row[1])
            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.contraseña))
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor= db.connection.cursor()
            sql="""SELECT  idusuario, usuario, contraseña FROM login
                    WHERE idusuario = '{}'""".format(id)
            cursor.execute(sql,)
            row = cursor.fetchone()
            print(row[1])
            if row != None:
                loged_user = User(row[0], row[1], None, row[2])
                return loged_user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
         