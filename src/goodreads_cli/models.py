from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class Author(BaseModel):
    id: int | None = None
    name: str | None = None
    profile_url: str | None = Field(default=None, alias="profileUrl")


class SearchItem(BaseModel):
    book_id: str = Field(alias="bookId")
    title: str
    book_url: str = Field(alias="bookUrl")
    avg_rating: float | None = Field(default=None, alias="avgRating")
    ratings_count: int | None = Field(default=None, alias="ratingsCount")
    author: Author | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")

    @field_validator("avg_rating", mode="before")
    @classmethod
    def _parse_avg_rating(cls, value: Any) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class BookDetails(BaseModel):
    book_id: str
    title: str
    url: str
    image_url: str | None = None
    description: str | None = None
    author_id: int | None = None
    author_name: str | None = None
    avg_rating: float | None = None
    ratings_count: int | None = None
    pages: int | None = None
    format: str | None = None
    publisher: str | None = None
    isbn: str | None = None
    isbn13: str | None = None
    language: str | None = None


class ShelfItem(BaseModel):
    title: str
    link: str
    book_id: str
    author: str | None = None
    average_rating: float | None = None
    rating: int | None = None
    read_at: str | None = None
    date_added: str | None = None
    date_created: str | None = None
    date_started: str | None = None
    shelves: list[str] = []
    review: str | None = None
    image_url: str | None = None
    book_published: str | None = None
    pages: int | None = None
    isbn: str | None = None


class ReadingTimelineEntry(BaseModel):
    title: str
    book_id: str
    pages: int | None = None
    started_at: str | None = None
    finished_at: str | None = None
    shelves: list[str] = []


class UserInfo(BaseModel):
    user_id: str
    name: str
    profile_url: str | None = None
