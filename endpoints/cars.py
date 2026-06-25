from itertools import count

from fastapi import APIRouter, HTTPException, status

from schemas.cars import Car, CarIn, CarPatch

router = APIRouter(prefix="/cars", tags=["cars"])

_cars: dict[int, Car] = {}
_ids = count(1)


def _get(car_id: int) -> Car:
    car = _cars.get(car_id)
    if car is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Car {car_id} not found")
    return car


@router.get("", response_model=list[Car])
def list_cars() -> list[Car]:
    return list(_cars.values())


@router.post("", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(payload: CarIn) -> Car:
    car = Car(id=next(_ids), **payload.model_dump())
    _cars[car.id] = car
    return car


@router.get("/{car_id}", response_model=Car)
def get_car(car_id: int) -> Car:
    return _get(car_id)


@router.put("/{car_id}", response_model=Car)
def replace_car(car_id: int, payload: CarIn) -> Car:
    _get(car_id)
    car = Car(id=car_id, **payload.model_dump())
    _cars[car_id] = car
    return car


@router.patch("/{car_id}", response_model=Car)
def patch_car(car_id: int, payload: CarPatch) -> Car:
    car = _get(car_id)
    updated = car.model_copy(update=payload.model_dump(exclude_unset=True))
    _cars[car_id] = updated
    return updated


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int) -> None:
    _get(car_id)
    del _cars[car_id]
