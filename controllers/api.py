#%%
from fastapi import FastAPI

fastapi_app = FastAPI(title="Get weather data")

@fastapi_app.get("/status")
def get_status(): 
    return {"status": "running"}

@fastapi_app.post("/{city}/weather")
def get_forecast(city: str): 
    return f"Sunny in {city}"

@fastapi_app.post("{city}/temperature")
def get_temperature(city: str):
    return f"Temperature in {city} is 25 degrees Celsius"

#%%
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
    
# %%
