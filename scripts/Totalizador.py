def actualizar():
	base = "[default]LACT_Bateria_1/"
	CAPACIDAD = 50.0   # m3 del tanque
	DT = 1.0           # s, igual al periodo del timer
	
	valores = system.tag.readBlocking([
		base + "Nivel_Tanque",
		base + "Sensores/Caudal_Ingreso",
		base + "Caudal_Bruto",
		base + "Valvula_Desviadora"
	])
	nivel, q_ingreso, q_bomba, entregando = [v.value for v in valores]
	
	if nivel is None or q_ingreso is None or q_bomba is None:
		return
	
	# Si recircula, lo que bombea vuelve al tanque: salida neta 0
	q_salida = q_bomba if entregando else 0.0
	
	delta_m3 = (q_ingreso - q_salida) / 3600.0 * DT
	nivel += delta_m3 / CAPACIDAD * 100.0
	nivel = max(0.0, min(100.0, nivel))
	
	system.tag.writeBlocking([base + "Nivel_Tanque"], [round(nivel, 2)])