from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS para acceso desde frontend

# Cargar datos CSV al iniciar
csv_path = os.path.join('data', 'MEN_MATRICULA_ESTADISTICA_ES_20250916.csv')
# Leer el CSV como texto y limpiar comas antes de convertir a numérico
df = pd.read_csv(csv_path, encoding='utf-8', dtype=str)  # Leer todo como string inicialmente
for col in ['Id Género', 'Total Matriculados', 'Año']:
    df[col] = df[col].str.replace(',', '').replace('', '0')  # Eliminar comas y manejar vacíos
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)  # Convertir a entero
df = df[df['Total Matriculados'] > 0]  # Filtrar registros vacíos

# Endpoint principal: Servir la página HTML
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint: Opciones para filtros dinámicos
@app.route('/api/filtros')
def get_filtros():
    tipo = request.args.get('tipo')
    opciones = []
    if tipo == 'institucion':
        opciones = sorted(df['Institución de Educación Superior (IES)'].unique().tolist())
    elif tipo == 'programa':
        opciones = sorted(df['Programa Académico'].unique().tolist())
    elif tipo == 'departamento':
        opciones = sorted(df['Departamento de oferta del programa'].unique().tolist())
    elif tipo == 'año':
        opciones = sorted(df['Año'].unique().tolist(), reverse=True)
    elif tipo == 'genero':
        opciones = [{'id': 1, 'label': 'Hombres'}, {'id': 2, 'label': 'Mujeres'}]
    elif tipo == 'municipio':
        opciones = sorted(df['Municipio de oferta del programa'].unique().tolist())
    return jsonify({'opciones': opciones})

# Endpoint: Datos filtrados para gráficos
@app.route('/api/datos-filtrados')
def get_datos_filtrados():
    filtros = {
        'institucion': request.args.get('institucion'),
        'programa': request.args.get('programa'),
        'departamento': request.args.get('departamento'),
        'año': request.args.get('año'),
        'genero': request.args.get('genero'),
        'municipio': request.args.get('municipio')
    }
    group_by = request.args.get('groupBy', 'Año')

    filtered_df = df.copy()
    for key, value in filtros.items():
        if value:
            if key == 'genero':
                filtered_df = filtered_df[filtered_df['Id Género'] == int(value)]
            elif key == 'año':
                filtered_df = filtered_df[filtered_df['Año'] == int(value)]
            else:
                filtered_df = filtered_df[filtered_df[key] == value]

    agrupado = filtered_df.groupby(group_by)['Total Matriculados'].sum().reset_index()
    labels = agrupado[group_by].tolist()
    values = agrupado['Total Matriculados'].tolist()

    return jsonify({'labels': labels, 'values': values, 'totalRegistros': len(filtered_df)})

# Endpoint: Resumen general
@app.route('/api/resumen')
def get_resumen():
    total_matriculas = df['Total Matriculados'].sum()
    por_año = df.groupby('Año')['Total Matriculados'].sum().to_dict()
    return jsonify({'totalMatriculas': int(total_matriculas), 'porAño': por_año})

if __name__ == '__main__':
    app.run(debug=True, port=5000)