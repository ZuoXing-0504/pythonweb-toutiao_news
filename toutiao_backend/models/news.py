from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Index, Text, ForeignKey

from models.base import Base, TimestampMixin, utc_now


class Category(TimestampMixin, Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类ID")
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    def __repr__(self) -> str:
        return f"<Category id={self.id}, name={self.name}, sort_order={self.sort_order}>"


# 新闻

class News(TimestampMixin, Base):
    __tablename__ = "news"
    # 创建索引：提升查询速度
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),#高频查询分类ID
        Index('idx_publish_time', 'publish_time')#高频查询发布时间
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement = True, comment = "新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment = "新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment = "新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封⾯图⽚URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False,comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=utc_now, comment = "发布时间")
    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
