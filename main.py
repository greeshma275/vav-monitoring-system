# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
import time
import threading
import uvicorn
from typing import List, Optional

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Benak@2010',  # Change this
    'database': 'vav_monitoring_system'
}

# Pydantic models
class VAVData(BaseModel):
    data_id: Optional[int]
    vav_unit: str
    parameter_name: str
    parameter_value: float
    timestamp: Optional[datetime]

class TempSetpointUpdate(BaseModel):
    vav_unit: str
    new_value: float

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Background task to update Temp_Setpoint values
from decimal import Decimal, getcontext

def update_temp_setpoints():
    getcontext().prec = 4  # Set decimal precision
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT data_id, vav_unit, parameter_value 
                FROM vav_data 
                WHERE parameter_name = 'Temp_Setpoint'
            """)
            setpoints = cursor.fetchall()
            
            for sp in setpoints:
                # Perform Decimal arithmetic
                current_value = sp['parameter_value']  # Already Decimal
                new_value = current_value + Decimal('0.5')
                
                cursor.execute("""
                    UPDATE vav_data 
                    SET parameter_value = %s, timestamp = NOW() 
                    WHERE data_id = %s
                """, (float(new_value), sp['data_id']))  # Convert back to float for MySQL
                conn.commit()
                
                print(f"Updated {sp['vav_unit']} Temp_Setpoint from {current_value} to {new_value}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error in background task: {e}")
        
        time.sleep(10)

# Start background thread when app starts
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=update_temp_setpoints)
    thread.daemon = True
    thread.start()

# API Endpoints
@app.get("/vav-data", response_model=List[VAVData])
def get_all_vav_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT data_id, vav_unit, parameter_name, parameter_value, timestamp
            FROM vav_data
            ORDER BY vav_unit, parameter_name
        """)
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temp-setpoints", response_model=List[VAVData])
def get_temp_setpoints():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT data_id, vav_unit, parameter_name, parameter_value, timestamp
            FROM vav_data
            WHERE parameter_name = 'Temp_Setpoint'
            ORDER BY vav_unit
        """)
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update-temp-setpoint")
def update_temp_setpoint(update: TempSetpointUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE vav_data 
            SET parameter_value = %s, timestamp = NOW()
            WHERE vav_unit = %s AND parameter_name = 'Temp_Setpoint'
        """, (update.new_value, update.vav_unit))
        
        conn.commit()
        affected_rows = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="VAV unit or parameter not found")
        
        return {"message": f"Temp_Setpoint for {update.vav_unit} updated to {update.new_value}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)