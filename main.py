from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import math
import os


app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
# 거리 구하는 함수
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# 데이터 로드
Busan_bus = []
try:
    with open("국토교통부_전국 버스정류장 위치정보_20241028.csv", "r", encoding="euc-kr") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[7] == "부산광역시":
                Busan_bus.append([row[0], row[1], float(row[2]), float(row[3])])
except FileNotFoundError:
    raise FileNotFoundError("버스 정류장 CSV 파일을 찾을 수 없습니다.")

# 요청
class LocationRequest(BaseModel):
    latitude: float  # 위도
    longitude: float  # 경도

# API 엔드포인트
@app.post("/nearest_bus_stops/")
def get_nearest_bus_stops(request: LocationRequest):
    w = request.latitude
    g = request.longitude
    res = []
    # 이상한 값 입력 방지
    if not (-90 <= w <= 90) or not (-180 <= g <= 180):
        raise HTTPException(status_code=400, detail="유효하지 않은 위도 또는 경도입니다.")

    # 가장 가까운 3개 정류장 계산
    for i in Busan_bus:
        try:
            now = haversine(w,g,float(i[2]),float(i[3]))
            res.append([now,i])
        except:
            pass
    res.sort(key = lambda x : (x[0]))
    idx = 0
    cnt = 0
    before = []
    result = []
    while cnt < 3:
        if not res[idx][1][1] in before:
            cnt += 1
            result.append(('정류장 : %s' %(res[idx][1][1]), '거리 : %.2fkm' %(res[idx][0])))
            before.append(res[idx][1][1])
        idx += 1

    # 결과 반환
    return {"현재 위치에서 가장 가까운 3개의 버스 정류장": result}
