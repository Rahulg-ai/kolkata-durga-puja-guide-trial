import json
import os
import secrets
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import (
    TrustedHostMiddleware,
)

from pydantic import (
    BaseModel,
    Field,
)

from slowapi import (
    Limiter,
    _rate_limit_exceeded_handler,
)

from slowapi.errors import (
    RateLimitExceeded,
)

from slowapi.util import (
    get_remote_address,
)


# ==================================================
# DATABASE
# ==================================================

from backend.database import (
    init_database,
)


# ==================================================
# DONATION / RAZORPAY FUNCTIONS
# ==================================================

from backend.donations import (
    ADMIN_TOKEN,
    RAZORPAY_WEBHOOK_SECRET,
    check_name,
    create_donation_order,
    get_admin_supporters,
    get_leaderboard,
    get_razorpay_client,
    process_razorpay_webhook,
    set_supporter_visibility,
    ensure_supporter_visibility_column,
    verify_donation,
)


# ==================================================
# ROUTING
# ==================================================

from scripts.routing.return_router import (
    build_return_route,
)

from scripts.routing.route_planner import (
    build_puja_route,
)


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)


load_dotenv(
    BASE_DIR / ".env"
)


# ==================================================
# APP
# ==================================================

app = FastAPI(
    title="Durga Puja Metro Guide",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

init_database()

ensure_supporter_visibility_column()


# ==================================================
# RATE LIMITING
# ==================================================

limiter = Limiter(
    key_func=get_remote_address
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# ==================================================
# HOST SECURITY
# ==================================================

allowed_hosts = [
    "localhost",
    "127.0.0.1",
]


production_host = os.getenv(
    "PRODUCTION_HOST"
)


if production_host:

    allowed_hosts.append(
        production_host
    )


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)


# ==================================================
# CORS
# ==================================================

frontend_origin = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        frontend_origin,

        "http://localhost:5173",

        "http://127.0.0.1:5173",

        "http://localhost:5174",

        "http://127.0.0.1:5174",
    ],

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "OPTIONS",
    ],

    allow_headers=[
        "Content-Type",
        "X-Admin-Token",
    ],
)


# ==================================================
# SECURITY HEADERS
# ==================================================

@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next,
):

    response = await call_next(
        request
    )


    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"


    response.headers[
        "X-Frame-Options"
    ] = "DENY"


    response.headers[
        "Referrer-Policy"
    ] = (
        "strict-origin-when-cross-origin"
    )


    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )


    return response


# ==================================================
# DATA FILES
# ==================================================

PANDAL_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "pandal_metro_mapping.csv"
)


METRO_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "metro_network_2026_cleaned.csv"
)


pandals = pd.read_csv(
    PANDAL_FILE
)


metro = pd.read_csv(
    METRO_FILE
)


# ==================================================
# REQUEST MODELS
# ==================================================

class RouteRequest(
    BaseModel
):

    start_station: str = Field(
        min_length=1,
        max_length=100,
    )

    selected_pandals: list[str] = Field(
        min_length=1,
        max_length=20,
    )


class ReturnRouteRequest(
    BaseModel
):

    current_pandal: str = Field(
        min_length=1,
        max_length=150,
    )

    start_station: str = Field(
        min_length=1,
        max_length=100,
    )


class DonationRequest(
    BaseModel
):

    display_name: str = Field(
        min_length=2,
        max_length=30,
    )

    amount: int = Field(
        ge=1,
        le=100000,
    )


class DonationVerificationRequest(
    BaseModel
):

    order_id: str = Field(
        min_length=1,
        max_length=100,
    )

    payment_id: str = Field(
        min_length=1,
        max_length=100,
    )

    signature: str = Field(
        min_length=1,
        max_length=300,
    )


# ==================================================
# ADMIN AUTHENTICATION
# ==================================================

def require_admin_token(
    request: Request,
):

    if not ADMIN_TOKEN:

        raise ValueError(
            "Admin token is not configured."
        )


    provided_token = (
        request.headers.get(
            "X-Admin-Token",
            "",
        )
    )


    if not provided_token:

        raise ValueError(
            "Missing admin token."
        )


    if not secrets.compare_digest(
        provided_token,
        ADMIN_TOKEN,
    ):

        raise ValueError(
            "Invalid admin token."
        )


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message":
            "Welcome to Durga Puja Metro Guide!"
    }


# ==================================================
# METRO STATIONS
# ==================================================

@app.get("/stations")
def get_stations():

    lines = {}


    for line, group in metro.groupby(
        "line"
    ):

        group = group.sort_values(
            "sequence"
        )


        lines[line] = (
            group["station_name"]
            .drop_duplicates()
            .tolist()
        )


    return {
        "lines":
            lines
    }


# ==================================================
# PANDALS
# ==================================================

@app.get("/pandals")
def get_pandals():

    return pandals.to_dict(
        orient="records"
    )


# ==================================================
# MAIN ROUTE
# ==================================================

@app.post("/route")
@limiter.limit("20/minute")
def create_route(
    request: Request,
    route_request: RouteRequest,
):

    route = build_puja_route(
        route_request.start_station,
        route_request.selected_pandals,
    )


    return {
        "start_station":
            route_request.start_station,

        "route":
            route,
    }


# ==================================================
# RETURN ROUTE
# ==================================================

@app.post("/return-route")
@limiter.limit("20/minute")
def create_return_route(
    request: Request,
    route_request: ReturnRouteRequest,
):

    result = build_return_route(
        route_request.current_pandal,
        route_request.start_station,
    )


    if result is None:

        return {
            "success":
                False,

            "message":
                "Return route could not be found.",
        }


    return {
        "success":
            True,

        "return_route":
            result,
    }


# ==================================================
# CHECK SUPPORTER NAME
# ==================================================

@app.get("/supporters/check-name")
@limiter.limit("30/minute")
def check_supporter_name(
    request: Request,
    name: str,
):

    name = name.strip()


    if not name:

        return {
            "available":
                False
        }


    if len(name) > 30:

        return {
            "available":
                False
        }


    return {
        "available":
            check_name(name)
    }


# ==================================================
# CREATE RAZORPAY ORDER
# ==================================================

@app.post("/donations/create-order")
@limiter.limit("5/minute")
def create_donation(
    request: Request,
    donation_request: DonationRequest,
):

    try:

        order = create_donation_order(
            donation_request.display_name,
            donation_request.amount,
        )


        return {
            "success":
                True,

            "order":
                order,
        }


    except ValueError as error:

        return {
            "success":
                False,

            "message":
                str(error),
        }


    except Exception as error:

        print(
            "RAZORPAY ORDER ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Unable to create payment order.",
        }


# ==================================================
# PAYMENT VERIFICATION
# ==================================================

@app.post("/donations/verify")
@limiter.limit("10/minute")
def verify_donation_payment(
    request: Request,
    donation_request:
        DonationVerificationRequest,
):

    try:

        result = verify_donation(
            donation_request.order_id,
            donation_request.payment_id,
            donation_request.signature,
        )


        return result


    except ValueError as error:

        return {
            "success":
                False,

            "message":
                str(error),
        }


    except Exception as error:

        print(
            "PAYMENT VERIFICATION ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Payment verification failed.",
        }


# ==================================================
# RAZORPAY WEBHOOK
# ==================================================

@app.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
):

    raw_body = await request.body()


    signature = request.headers.get(
        "X-Razorpay-Signature"
    )


    event_id = request.headers.get(
        "x-razorpay-event-id"
    )


    if not signature:

        return {
            "success":
                False,

            "message":
                "Missing webhook signature.",
        }


    if not event_id:

        return {
            "success":
                False,

            "message":
                "Missing webhook event ID.",
        }


    if not RAZORPAY_WEBHOOK_SECRET:

        return {
            "success":
                False,

            "message":
                "Webhook secret not configured.",
        }


    # --------------------------------------------------
    # VERIFY RAZORPAY WEBHOOK SIGNATURE
    # --------------------------------------------------

    try:

        client = (
            get_razorpay_client()
        )


        client.utility.verify_webhook_signature(
            raw_body.decode(
                "utf-8"
            ),
            signature,
            RAZORPAY_WEBHOOK_SECRET,
        )


    except Exception as error:

        print(
            "WEBHOOK SIGNATURE ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Invalid webhook signature.",
        }


    # --------------------------------------------------
    # PARSE EVENT
    # --------------------------------------------------

    try:

        payload = json.loads(
            raw_body.decode(
                "utf-8"
            )
        )


        event_name = payload.get(
            "event",
            "",
        )


        result = process_razorpay_webhook(
            event_name,
            payload,
            event_id,
        )


        return {
            "success":
                True,

            "result":
                result,
        }


    except Exception as error:

        print(
            "WEBHOOK PROCESSING ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Webhook processing failed.",
        }


# ==================================================
# PUBLIC SUPPORTER LEADERBOARD
# ==================================================

@app.get("/supporters")
@limiter.limit("60/minute")
def supporters(
    request: Request,
):

    return {
        "supporters":
            get_leaderboard()
    }


# ==================================================
# ADMIN - GET ALL SUPPORTERS
# ==================================================

@app.get("/admin/supporters")
@limiter.limit("30/minute")
def admin_supporters(
    request: Request,
):

    try:

        require_admin_token(
            request
        )


        return {
            "success":
                True,

            "supporters":
                get_admin_supporters(),
        }


    except ValueError as error:

        return {
            "success":
                False,

            "message":
                str(error),
        }


    except Exception as error:

        print(
            "ADMIN SUPPORTER ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Unable to load supporters.",
        }


# ==================================================
# ADMIN - HIDE / SHOW SUPPORTER
# ==================================================

@app.patch(
    "/admin/supporters/{supporter_id}/visibility"
)
@limiter.limit("30/minute")
def admin_set_supporter_visibility(
    request: Request,
    supporter_id: int,
    visible: bool,
):

    try:

        require_admin_token(
            request
        )


        result = set_supporter_visibility(
            supporter_id,
            visible,
        )


        return result


    except ValueError as error:

        return {
            "success":
                False,

            "message":
                str(error),
        }


    except Exception as error:

        print(
            "ADMIN VISIBILITY ERROR:",
            repr(error),
        )


        return {
            "success":
                False,

            "message":
                "Unable to update supporter visibility.",
        }