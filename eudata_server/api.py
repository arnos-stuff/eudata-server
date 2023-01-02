import json
import rich
import pandas as pd
from functools import reduce
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.exceptions import (
    RequestValidationError, HTTPException, ValidationError
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from eudata_server.backend.sdmx.base import (
    dfquery, get_time_period,
    get_text_unit, setup_chrmap
)

from eudata_server.tools.paths import (
    static_dir, templates_dir, css_dir,
    js_dir, sass_dir, data_dir, package_dir
)
# config
cfg_fname = package_dir / "config.json"

if cfg_fname.exists():
    config = json.load(open(cfg_fname, "r"))
else:
    config = {}
# Mount static files & templates

app = FastAPI()

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/css", StaticFiles(directory=css_dir), name="css")
app.mount("/js", StaticFiles(directory=js_dir), name="js")
app.mount("/{rest:path}/static", StaticFiles(directory=static_dir), name="static")
app.mount("/{rest:path}/css", StaticFiles(directory=css_dir), name="css")
app.mount("/{rest:path}/js", StaticFiles(directory=js_dir), name="js")
templates = Jinja2Templates(directory=templates_dir)

# get metadata
units_path = data_dir / "units.json"
catscheme_path = data_dir / "toc-cat-schemes.json"
categories = json.load(open(catscheme_path,"r"))
catnames = reduce(                                                                                                                                                                                                                                                                                                                                                 
    lambda acc, new: acc + [new] if new not in acc else acc,
    [c["category_scheme_name"] for c in categories],
    []
    )

dfu = pd.read_json(units_path, orient="records")

# add routes

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/toc", response_class=HTMLResponse)
async def toc(request: Request):
    return templates.TemplateResponse("grid-toc.html",
    {
        "request": request,
        "categories": categories,
        "catnames": sorted(catnames),
        "title": "Table of Contents",
        }
    )

@app.get("/tab/{dataflow_id}", response_class=HTMLResponse)
async def tab(request: Request, dataflow_id: str):
    df = dfquery(dataflow_id)
    columns = df.columns.tolist()
    rows = df.to_dict(orient="records")

    return templates.TemplateResponse("grid-dataset.html",
    {
        "request": request,
        "dataflow_id": dataflow_id,
        "title": f"Dataset {dataflow_id}",
        "columns": columns,
        "rows": rows,
        })

@app.get("/maps/{dataflow_id}", response_class=HTMLResponse)
async def maps(request: Request, dataflow_id: str):
    # try:
    df = dfquery(dataflow_id)
    mapdata = setup_chrmap(df)

    u_names = dfu.to_dict(orient="records")
    
    unit_names = {}
    for u in u_names:
        if u["code"] in mapdata["units"]:
            unit_names[u["code"]] = u["description"]

    # except Exception as err:
    #     print(err)
    #     raise StarletteHTTPException(status_code=500, detail="Woops ! No data found.")

    return templates.TemplateResponse(
        "maps.html",
        {
            "request": request,
            "dataflow_id": dataflow_id,
            "title": "Maps",
            "unit_names": unit_names,
            **mapdata,
        }
    )

@app.exception_handler(StarletteHTTPException)
async def exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_number": exc.status_code,
            "error_message": exc.detail,
        },
        status_code=exc.status_code,
    )