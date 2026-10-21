# bungeo-weather

붕어빵 장사(`bungeo`) 앱이 읽는 날씨 파일. 기상청 초단기실황(공공데이터포털) 8개 도시 기온·강수형태를 1시간마다 `weather.json` 으로 갱신한다.
앱은 `https://raw.githubusercontent.com/wing40/bungeo-weather/main/weather.json` 한 파일만 읽고, 6시간 넘게 낡으면 평년 기온으로 폴백한다. 출처: 기상청.
