"""Comment and review system for collaborative editing."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ReviewStatus(Enum):
    """Status of reviews."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


@dataclass
class Comment:
    """Represents a comment on a diagram element."""

    comment_id: str
    author_id: str
    author_name: str
    content: str
    element_id: Optional[str]
    position: Optional[Dict[str, float]]
    created_at: datetime
    updated_at: datetime
    is_resolved: bool = False
    parent_comment_id: Optional[str] = None

    def __post_init__(self):
        if not self.comment_id:
            self.comment_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "comment_id": self.comment_id,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "content": self.content,
            "element_id": self.element_id,
            "position": self.position,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_resolved": self.is_resolved,
            "parent_comment_id": self.parent_comment_id,
        }


@dataclass
class CommentThread:
    """Represents a thread of comments."""

    thread_id: str
    root_comment_id: str
    comments: List[Comment] = field(default_factory=list)
    is_resolved: bool = False

    def add_comment(self, comment: Comment) -> None:
        self.comments.append(comment)

    def resolve_thread(self) -> None:
        self.is_resolved = True
        for comment in self.comments:
            comment.is_resolved = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "root_comment_id": self.root_comment_id,
            "comments": [c.to_dict() for c in self.comments],
            "is_resolved": self.is_resolved,
        }


@dataclass
class Review:
    """Represents a review of diagram changes."""

    review_id: str
    reviewer_id: str
    reviewer_name: str
    commit_id: str
    status: ReviewStatus
    summary: str
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = field(default_factory=list)

    def __post_init__(self):
        if not self.review_id:
            self.review_id = str(uuid.uuid4())

    def add_comment(self, comment: Comment) -> None:
        self.comments.append(comment)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "reviewer_id": self.reviewer_id,
            "reviewer_name": self.reviewer_name,
            "commit_id": self.commit_id,
            "status": self.status.value,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "comments": [c.to_dict() for c in self.comments],
        }


class CommentSystem:
    """Manages comments and reviews for collaborative editing."""

    def __init__(self):
        self.comments: Dict[str, Comment] = {}
        self.threads: Dict[str, CommentThread] = {}
        self.reviews: Dict[str, Review] = {}

    def add_comment(
        self,
        author_id: str,
        author_name: str,
        content: str,
        element_id: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        parent_comment_id: Optional[str] = None,
    ) -> Comment:
        """Add a new comment."""
        now = datetime.now()

        comment = Comment(
            comment_id=str(uuid.uuid4()),
            author_id=author_id,
            author_name=author_name,
            content=content,
            element_id=element_id,
            position=position,
            created_at=now,
            updated_at=now,
            parent_comment_id=parent_comment_id,
        )

        self.comments[comment.comment_id] = comment

        # Handle threading
        if parent_comment_id:
            # Find existing thread or create new one
            thread = self._find_thread_for_comment(parent_comment_id)
            if thread:
                thread.add_comment(comment)
            else:
                # Create new thread
                thread_id = str(uuid.uuid4())
                thread = CommentThread(
                    thread_id=thread_id,
                    root_comment_id=parent_comment_id,
                )
                thread.add_comment(comment)
                self.threads[thread_id] = thread
        else:
            # Root comment - create new thread
            thread_id = str(uuid.uuid4())
            thread = CommentThread(
                thread_id=thread_id,
                root_comment_id=comment.comment_id,
            )
            thread.add_comment(comment)
            self.threads[thread_id] = thread

        return comment

    def update_comment(self, comment_id: str, content: str) -> bool:
        """Update an existing comment."""
        if comment_id not in self.comments:
            return False

        comment = self.comments[comment_id]
        comment.content = content
        comment.updated_at = datetime.now()

        return True

    def resolve_comment(self, comment_id: str) -> bool:
        """Resolve a comment."""
        if comment_id not in self.comments:
            return False

        comment = self.comments[comment_id]
        comment.is_resolved = True
        comment.updated_at = datetime.now()

        # Resolve thread if this is the root comment
        thread = self._find_thread_for_comment(comment_id)
        if thread and thread.root_comment_id == comment_id:
            thread.resolve_thread()

        return True

    def create_review(
        self,
        reviewer_id: str,
        reviewer_name: str,
        commit_id: str,
        status: ReviewStatus,
        summary: str,
    ) -> Review:
        """Create a new review."""
        now = datetime.now()

        review = Review(
            review_id=str(uuid.uuid4()),
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            commit_id=commit_id,
            status=status,
            summary=summary,
            created_at=now,
            updated_at=now,
        )

        self.reviews[review.review_id] = review
        return review

    def update_review_status(self, review_id: str, status: ReviewStatus) -> bool:
        """Update review status."""
        if review_id not in self.reviews:
            return False

        review = self.reviews[review_id]
        review.status = status
        review.updated_at = datetime.now()

        return True

    def get_comments_for_element(self, element_id: str) -> List[Comment]:
        """Get all comments for a specific element."""
        return [
            comment
            for comment in self.comments.values()
            if comment.element_id == element_id and not comment.is_resolved
        ]

    def get_reviews_for_commit(self, commit_id: str) -> List[Review]:
        """Get all reviews for a specific commit."""
        return [
            review for review in self.reviews.values() if review.commit_id == commit_id
        ]

    def _find_thread_for_comment(self, comment_id: str) -> Optional[CommentThread]:
        """Find the thread containing a specific comment."""
        for thread in self.threads.values():
            if any(c.comment_id == comment_id for c in thread.comments):
                return thread
        return None
