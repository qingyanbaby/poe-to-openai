import uvicorn
from main import app

uvicorn.run(app, host='0.0.0.0',
            port=39527,
            proxy_headers=True,
            forwarded_allow_ips='*',
            )
