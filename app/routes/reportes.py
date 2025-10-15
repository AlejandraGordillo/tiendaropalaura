from flask import Blueprint, jsonify, request
from app.models import reportes
from datetime import datetime
from app.models.reportes import Reporte
from app.models.usuarios import  User


# Blueprint para manejar los reportes
reportes_bp = Blueprint('reportes', __name__)

# 🔹 Reporte general
@reportes_bp.route('/reportes', methods=['GET'])
def obtener_reportes():
    reportes = Reporte.query.order_by(Reporte.fecha_generacion.desc()).all()

    data = []
    for reporte in reportes:
        usuario = User.query.get(reporte.idUser)

        detalles = [
            {
                'idDetalleReporte': d.idDetalleReporte,
                'idPedido': d.idPedido,
                'descripcion': d.descripcion,
                'monto': float(d.monto)
            }
            for d in reporte.detalles
        ]

        data.append({
            'idReporte': reporte.idReporte,
            'usuario': usuario.nameUser if usuario else 'Usuario eliminado',
            'fecha_generacion': reporte.fecha_generacion.strftime('%Y-%m-%d %H:%M'),
            'tipo': reporte.tipo,
            'total_pedidos': reporte.total_pedidos,
            'total_ventas': float(reporte.total_ventas),
            'observaciones': reporte.observaciones,
            'detalles': detalles
        })
    return jsonify(data)


# 🔹 Reporte filtrado por fecha
@reportes_bp.route('/reportes/fecha', methods=['GET'])
def obtener_reportes_por_fecha():
    fecha_inicio = request.args.get('inicio')
    fecha_fin = request.args.get('fin')

    if not fecha_inicio or not fecha_fin:
        return jsonify({'error': 'Debes enviar las fechas inicio y fin en formato YYYY-MM-DD'}), 400

    try:
        inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha incorrecto (usa YYYY-MM-DD)'}), 400

    reportes = Reporte.query.filter(
        Reporte.fecha_generacion.between(inicio, fin)
    ).order_by(Reporte.fecha_generacion.desc()).all()

    data = [{
        'idReporte': r.idReporte,
        'usuario': User.query.get(r.idUser).nameUser if User.query.get(r.idUser) else 'Usuario eliminado',
        'fecha_generacion': r.fecha_generacion.strftime('%Y-%m-%d %H:%M'),
        'tipo': r.tipo,
        'total_pedidos': r.total_pedidos,
        'total_ventas': float(r.total_ventas),
        'observaciones': r.observaciones
    } for r in reportes]

    return jsonify(data)


# 🔹 Reporte por usuario
@reportes_bp.route('/reportes/usuario/<int:idUser>', methods=['GET'])
def obtener_reportes_por_usuario(idUser):
    reportes = Reporte.query.filter_by(idUser=idUser).order_by(Reporte.fecha_generacion.desc()).all()

    data = [{
        'idReporte': r.idReporte,
        'fecha_generacion': r.fecha_generacion.strftime('%Y-%m-%d %H:%M'),
        'tipo': r.tipo,
        'total_pedidos': r.total_pedidos,
        'total_ventas': float(r.total_ventas),
        'observaciones': r.observaciones
    } for r in reportes]

    return jsonify(data)


# 🔹 Detalles de un reporte específico
@reportes_bp.route('/reportes/<int:idReporte>/detalles', methods=['GET'])
def obtener_detalles_reporte(idReporte):
    reporte = Reporte.query.get(idReporte)

    if not reporte:
        return jsonify({'error': 'Reporte no encontrado'}), 404

    detalles = [{
        'idDetalleReporte': d.idDetalleReporte,
        'idPedido': d.idPedido,
        'descripcion': d.descripcion,
        'monto': float(d.monto)
    } for d in reporte.detalles]

    return jsonify({
        'idReporte': reporte.idReporte,
        'tipo': reporte.tipo,
        'fecha_generacion': reporte.fecha_generacion.strftime('%Y-%m-%d %H:%M'),
        'total_pedidos': reporte.total_pedidos,
        'total_ventas': float(reporte.total_ventas),
        'detalles': detalles
    })
