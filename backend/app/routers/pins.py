"""
Pins router - provides job marker data for the map.
"""

from fastapi import APIRouter
from ..models import JobPin, JobPinResponse

router = APIRouter(prefix="/pins", tags=["pins"])

# Sample job marker data across major Indian cities
SAMPLE_PINS: list[JobPin] = [
    JobPin(
        id="1",
        company_name="Tata Consultancy Services",
        job_title="Software Engineer",
        latitude=19.0760,
        longitude=72.8777,
        job_url="https://www.tcs.com/careers",
        location_name="Mumbai",
        description="Join India's largest IT services company"
    ),
    JobPin(
        id="2",
        company_name="Infosys",
        job_title="Full Stack Developer",
        latitude=12.9716,
        longitude=77.5946,
        job_url="https://www.infosys.com/careers",
        location_name="Bangalore",
        description="Work at the heart of India's tech hub"
    ),
    JobPin(
        id="3",
        company_name="Wipro",
        job_title="Data Analyst",
        latitude=28.6139,
        longitude=77.2090,
        job_url="https://careers.wipro.com",
        location_name="Delhi",
        description="Shape the future of digital transformation"
    ),
    JobPin(
        id="4",
        company_name="Microsoft India",
        job_title="Cloud Solutions Architect",
        latitude=17.3850,
        longitude=78.4867,
        job_url="https://careers.microsoft.com",
        location_name="Hyderabad",
        description="Build cloud solutions at scale"
    ),
    JobPin(
        id="5",
        company_name="Cognizant",
        job_title="Business Analyst",
        latitude=13.0827,
        longitude=80.2707,
        job_url="https://careers.cognizant.com",
        location_name="Chennai",
        description="Drive business innovation with technology"
    ),
    JobPin(
        id="6",
        company_name="Tech Mahindra",
        job_title="DevOps Engineer",
        latitude=18.5204,
        longitude=73.8567,
        job_url="https://careers.techmahindra.com",
        location_name="Pune",
        description="Automate and optimize software delivery"
    ),
]


@router.get("", response_model=JobPinResponse)
async def get_pins():
    """
    Get all job pins for map display.
    
    Returns a list of job markers with company information,
    coordinates, and job application links.
    """
    return JobPinResponse(pins=SAMPLE_PINS, total=len(SAMPLE_PINS))


@router.get("/{pin_id}", response_model=JobPin)
async def get_pin(pin_id: str):
    """
    Get a specific job pin by ID.
    """
    for pin in SAMPLE_PINS:
        if pin.id == pin_id:
            return pin
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Pin not found")
