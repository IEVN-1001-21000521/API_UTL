from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

con = MySQL(app)

@app.route("/alumnos", methods=['GET'])
def lista_alumnos():
    try:
        cursor = con.connection.cursor()
        sql = "SELECT * FROM alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                "matricula": fila[0],
                "nombre": fila[1],
                "aparterno": fila[2],
                "amaterno": fila[3],
                "correo": fila[4]
            }
            alumnos.append(alumno)
        return jsonify({"alumnos": alumnos, "mensaje": "lista de alumnos", "exito": True}), 200
    except Exception as ex:
        return jsonify({"message": f"error {ex}", "exito": False}), 500

def leer_alumno_bd(matricula):
    try:
        cursor = con.connection.cursor()
        sql = "SELECT * FROM alumnos WHERE matricula = %s"
        cursor.execute(sql, (matricula,))
        datos = cursor.fetchone()
        
        if datos:
            alumno = {
                "matricula": datos[0],
                "nombre": datos[1],
                "aparterno": datos[2],
                "amaterno": datos[3],
                "correo": datos[4]
            }
            return alumno
        else:
            return None
    except Exception as ex:
        return None

@app.route("/alumnos/<mat>", methods=['GET'])
def leer_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno:
            return jsonify({"alumno": alumno, "mensaje": "Alumno encontrado", "exito": True}), 200
        else:
            return jsonify({"alumno": None, "mensaje": "Alumno no encontrado", "exito": False}), 404
    except Exception as ex:
        return jsonify({"message": f"error {ex}", "exito": False}), 500
    

@app.route('/alumnos', methods=['POST'])
def registrar_alumno():
    try:
        alumno = leer_alumno_bd(request.json['matricula'])
        if alumno:
            return jsonify({"mensaje": "Alumno ya existe, no se puede duplicar", "exito": False}), 400
        else:
            cursor = con.connection.cursor()
            sql = """INSERT INTO alumnos (matricula, nombre, aparterno, amaterno, correo) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                request.json['matricula'],
                request.json['nombre'],
                request.json['aparterno'],
                request.json['amaterno'],
                request.json['correo']
            ))
            con.connection.commit()
            return jsonify({"mensaje": "Alumno registrado", "exito": True}), 201
    except Exception as ex:
        return jsonify({"mensaje": f"Error {ex}", "exito": False}), 500

@app.route('/alumnos/<mat>', methods=['PUT'])
def actualizar_curso(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno:
            cursor = con.connection.cursor()
            sql = """UPDATE alumnos SET nombre = %s, aparterno = %s, amaterno = %s, correo = %s WHERE matricula = %s"""
            cursor.execute(sql, (
                request.json['nombre'],
                request.json['aparterno'],
                request.json['amaterno'],
                request.json['correo'],
                mat
            ))
            con.connection.commit()
            return jsonify({'mensaje': "Alumno actualizado.", 'exito': True}), 200
        else:
            return jsonify({'mensaje': "Alumno no encontrado.", 'exito': False}), 404
    except Exception as ex:
        return jsonify({'mensaje': f"Error {ex}", 'exito': False}), 500
 
@app.route('/alumnos/<mat>', methods=['DELETE'])
def eliminar_curso(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno:
            cursor = con.connection.cursor()
            sql = "DELETE FROM alumnos WHERE matricula = %s"
            cursor.execute(sql, (mat,))
            con.connection.commit()
            return jsonify({'mensaje': "Alumno eliminado.", 'exito': True}), 200
        else:
            return jsonify({'mensaje': "Alumno no encontrado.", 'exito': False}), 404
    except Exception as ex:
        return jsonify({'mensaje': f"Error {ex}", 'exito': False}), 500

def pagina_no_encontrada(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)
