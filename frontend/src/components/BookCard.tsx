import React from 'react';
import { Star } from 'lucide-react';

interface BookCardProps {
  title: string;
  author: string;
  image: string;
  originalPrice?: number;
  salePrice?: number;
  rating?: number;
  reviews?: number;
  avg_rating?: number;
  reviews_count?: number;
  onClick?: () => void;
}

const BookCard: React.FC<BookCardProps> = ({
  title,
  author,
  image,
  originalPrice,
  salePrice,
  rating,
  reviews,
  avg_rating,
  reviews_count,
  onClick,
}) => {
  // Ưu tiên sử dụng avg_rating và reviews_count nếu có
  const displayRating = avg_rating !== undefined ? avg_rating : rating;
  const displayReviews = reviews_count !== undefined ? reviews_count : reviews;
  return (
    <div
      className="bg-white border rounded overflow-hidden cursor-pointer flex flex-col h-full"
      onClick={onClick}
      style={{ minHeight: '350px' }} // Đảm bảo chiều cao tối thiểu
    >
      <div className="h-48 flex items-center justify-center bg-gray-100">
        <img
          src={image}
          alt={title}
          onError={(e) => {
            // Khi ảnh lỗi, thay thế bằng ảnh mặc định
            e.currentTarget.src = '/covers/default.jpg';
          }}
          className="max-h-full max-w-full object-contain"
        />
      </div>
      <div className="p-4 flex flex-col flex-grow">
        {/* Tiêu đề và tác giả với chiều cao cố định */}
        <div className="min-h-[60px]">
          <h3 className="font-semibold truncate">{title}</h3>
          <p className="text-gray-600 text-sm">{author}</p>
        </div>

        {/* Rating section với chiều cao cố định */}
        <div className="h-8 flex items-center mt-2">
          {typeof displayRating === 'number' && displayRating > 0 ? (
            <>
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="ml-1 text-sm">{displayRating.toFixed(1)}</span>
              {typeof displayReviews === 'number' && displayReviews > 0 && (
                <span className="text-sm text-gray-500 ml-2">({displayReviews} reviews)</span>
              )}
            </>
          ) : (
            <span className="text-sm text-gray-400">No ratings yet</span>
          )}
        </div>

        {/* Phần giá luôn ở dưới cùng */}
        <div className="flex items-center mt-auto pt-4">
          {Number(originalPrice) > 0 && Number(originalPrice) !== Number(salePrice) ? (
            <>
              <span className="text-gray-400 line-through text-sm mr-2">
                ${Number(originalPrice).toFixed(2)}
              </span>
              <span className="text-gray-800 font-bold">
                ${Number(salePrice).toFixed(2)}
              </span>
            </>
          ) : (
            <span className="text-gray-800 font-bold">
              ${Number(salePrice).toFixed(2)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookCard;