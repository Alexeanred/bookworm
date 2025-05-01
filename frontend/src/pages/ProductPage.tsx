import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { booksApi } from "../services/api/books";
import { addToCart as addItemToCart, getCartItems } from "../services/cart";

type ProductPageProps = {
  cartCount: number;
  addToCart: (qty: number) => void;
};

interface BookDetail {
  id: number;
  title: string;
  summary: string;
  cover: string;
  original_price: number;
  discount_price?: number;
  final_price: number;
  discount_percent?: number;
  category: {
    id: number;
    name: string;
  };
  author: {
    id: number;
    name: string;
  };
  reviews_count?: number;
  avg_rating?: number;
}

const ProductPage: React.FC<ProductPageProps> = ({ addToCart }) => {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<BookDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentCartQuantity, setCurrentCartQuantity] = useState(0);

  // Fetch book details
  useEffect(() => {
    const fetchBookDetail = async () => {
      if (!id) return;

      try {
        setLoading(true);
        setError(null);
        const bookId = parseInt(id);
        const data = await booksApi.getBookDetail(bookId);

        // Log chi tiết về dữ liệu sách
        console.log('Book detail data:', data);
        console.log('Book price fields:', {
          original_price: data.original_price,
          price: data.price,
          discount_price: data.discount_price,
          final_price: data.final_price,
          price_final: data.price_final,
          sale_price: data.sale_price,
          book_detail: data.book_detail
        });

        // Sử dụng type assertion để tránh lỗi TypeScript
        setBook(data as any);
      } catch (err: any) {
        console.error('Error fetching book details:', err);
        setError(err.message || 'Failed to load book details');
      } finally {
        setLoading(false);
      }
    };

    fetchBookDetail();
  }, [id]);

  // Check current quantity in cart
  useEffect(() => {
    if (id) {
      const bookId = parseInt(id);
      const cartItems = getCartItems();
      const currentItem = cartItems.find(item => item.id === bookId);

      if (currentItem) {
        setCurrentCartQuantity(currentItem.quantity);
      } else {
        setCurrentCartQuantity(0);
      }
    }
  }, [id]);

  const handleAddToCart = () => {
    if (book) {
      // Check if adding this quantity would exceed the limit of 8
      const totalQuantity = currentCartQuantity + quantity;

      // If we already have items and adding more would exceed limit
      if (currentCartQuantity > 0 && totalQuantity > 8) {
        // Calculate how many more items can be added
        const remainingAllowed = 8 - currentCartQuantity;

        // If trying to add more than allowed
        if (quantity > remainingAllowed) {
          // Show error message
          setErrorMessage(`You already have ${currentCartQuantity} of this book in your cart. You can only add ${remainingAllowed} more.`);
          setShowError(true);
          setShowSuccess(false);
          setTimeout(() => setShowError(false), 4000);
          return;
        }
      }

      // If we reach here, it's safe to add to cart
      // Add to cart in localStorage and get actual quantity added
      const actualQtyAdded = addItemToCart(book, quantity);

      // Update cart count in header with actual quantity added
      addToCart(actualQtyAdded);

      // Update current cart quantity
      setCurrentCartQuantity(prev => prev + actualQtyAdded);

      // Show success message
      setShowSuccess(true);
      setShowError(false);
      setTimeout(() => setShowSuccess(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl text-red-600">{error || 'Book not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <div className="container mx-auto px-4">
        <div className="py-4 flex flex-col">
          <div className="text-3xl font-bold">
            <span className="mr-2">Category name:</span>
            <span className="text-gray-700">{book.category.name}</span>
          </div>
          <div className="border-b border-gray-300 mt-2"></div>
        </div>

        <div className="flex flex-col md:flex-row gap-6">
          {/* Left Column - Book Details with Image */}
          <div className="flex-1 border rounded-lg overflow-hidden">
            <div className="flex flex-col md:flex-row">
              {/* Book Image with Author */}
              <div className="w-full md:w-[200px] relative">
                <div className="bg-gray-100">
                  <img
                    src={book.cover ? `/covers/${book.cover}.jpg` : '/covers/default.jpg'}
                    alt={book.title}
                    onError={(e) => {
                      // Khi ảnh lỗi, thay thế bằng ảnh mặc định
                      e.currentTarget.src = '/covers/default.jpg';
                    }}
                    className="w-full h-auto object-contain"
                  />
                </div>
                <div className="text-sm text-gray-600 text-right p-2">
                  By (author) <span className="font-semibold">{book.author.name}</span>
                </div>
              </div>

              {/* Book Details */}
              <div className="flex-1 p-6">
                <div className="text-2xl font-bold mb-4">{book.title}</div>
                <div className="mb-2">
                  <span className="text-base font-semibold">Book description: </span>
                </div>
                <div className="text-base text-gray-700 mb-6">{book.summary}</div>

                {/* Book Features */}
                <div className="text-base text-gray-700">
                  <div className="font-semibold mb-1">"The multi-million copy bestseller"</div>
                  <div className="mb-1">Soon to be a major film</div>
                  <div className="mb-1">A Number One New York Times Bestseller</div>
                  <div className="mb-1">"Painfully beautiful" New York Times</div>
                  <div className="mb-1">Unforgettable... "as engrossing as it is moving" Daily Mail</div>
                  <div className="mb-1">"A rare achievement" The Times</div>
                  <div className="mb-1">"I can't even express how much I love this book!" Reese Witherspoon</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Price & Add to Cart */}
          <div className="w-full md:w-[350px] border rounded-lg overflow-hidden self-start">
            {/* Price */}
            <div className="p-4 bg-white">
              <div className="flex justify-between items-center">
                {/* Phần giá - hiển thị bên trái theo mockup */}
                <div className="text-left">
                  {(() => {
                    // Type assertion để tránh lỗi TypeScript
                    const bookAny = book as any;

                    console.log('Book data:', book);
                    console.log('Book any:', bookAny);

                    // Xử lý giá từ API

                    // Hàm chuyển đổi giá từ chuỗi hoặc số sang số
                    const parsePrice = (price: any): number => {
                      if (typeof price === 'number') return price;
                      if (typeof price === 'string') {
                        // Loại bỏ các ký tự không phải số và dấu chấm
                        const cleanPrice = price.replace(/[^0-9.]/g, '');
                        return parseFloat(cleanPrice) || 0;
                      }
                      return 0;
                    };

                    // Lấy giá gốc (original_price)
                    let originalPrice = 0;
                    if (bookAny.original_price) {
                      originalPrice = parsePrice(bookAny.original_price);
                    }

                    // Lấy giá cuối cùng (final_price)
                    let finalPrice = 0;
                    if (bookAny.final_price) {
                      finalPrice = parsePrice(bookAny.final_price);
                      console.log('Found final_price:', bookAny.final_price, 'parsed as:', finalPrice);
                    } else {
                      console.log('final_price not found in API response');
                    }

                    // Kiểm tra xem có giảm giá hay không
                    const hasDiscount = originalPrice > 0 && finalPrice > 0 && finalPrice < originalPrice;

                    // Nếu không tìm thấy finalPrice, sử dụng originalPrice
                    if (finalPrice <= 0 && originalPrice > 0) {
                      finalPrice = originalPrice;
                      console.log('Using originalPrice as finalPrice:', finalPrice);
                    }

                    // Tạo giá giảm giả cho mục đích demo (chỉ khi không có giảm giá thật)
                    // Bỏ comment dòng dưới đây để luôn hiển thị giá giảm theo mockup
                    // if (!hasDiscount && originalPrice > 0) {
                    //   finalPrice = originalPrice * 0.8; // Giảm 20%
                    //   console.log('Created fake discount for demo:', finalPrice);
                    // }

                    console.log('Price analysis:', {
                      originalPrice,
                      finalPrice,
                      hasDiscount
                    });

                    // Kiểm tra nếu có giá hợp lệ
                    if (originalPrice <= 0) {
                      // Nếu không tìm thấy giá hợp lệ, hiển thị thông báo
                      return (
                        <div className="text-2xl font-bold">
                          Price not available
                        </div>
                      );
                    } else if (hasDiscount) {
                      // Nếu có giảm giá - hiển thị theo mockup
                      console.log('Displaying discounted price:', { originalPrice, finalPrice });
                      return (
                        <div className="flex items-baseline">
                          <span className="line-through text-gray-500 text-lg mr-2">
                            ${originalPrice.toFixed(2)}
                          </span>
                          <span className="text-2xl font-bold text-black">
                            ${finalPrice.toFixed(2)}
                          </span>
                        </div>
                      );
                    } else {
                      // Nếu không có giảm giá
                      console.log('Displaying regular price:', originalPrice);
                      return (
                        <div className="text-2xl font-bold">
                          ${originalPrice.toFixed(2)}
                        </div>
                      );
                    }
                  })()}
                </div>
              </div>
            </div>

            {/* Divider - Full width */}
            <div className="border-t border-gray-200 w-full"></div>

            {/* Quantity and Add to Cart */}
            <div className="p-4 bg-white">
              <div className="mb-4">
                <div className="text-base mb-2">Quantity</div>
                {currentCartQuantity > 0 && (
                  <div className="text-sm text-blue-600 mb-2">
                    You already have {currentCartQuantity} of this book in your cart.
                    {currentCartQuantity < 8 && ` You can add up to ${8 - currentCartQuantity} more.`}
                  </div>
                )}
                <div className="flex items-center">
                  <button
                    className="px-3 py-2 bg-gray-200 border-gray-300 border rounded-l disabled:opacity-50"
                    onClick={() => setQuantity(q => Math.max(1, q - 1))}
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <input
                    type="text"
                    value={quantity}
                    readOnly
                    className="w-full text-center border-t border-b border-gray-300 py-2 text-base bg-gray-200"
                  />
                  <button
                    className="px-3 py-2 bg-gray-200 border-gray-300 border rounded-r disabled:opacity-50"
                    onClick={() => setQuantity(q => Math.min(8 - currentCartQuantity, q + 1))}
                    disabled={quantity >= 8 - currentCartQuantity || currentCartQuantity >= 8}
                  >
                    +
                  </button>
                </div>
              </div>

              <button
                className="w-full bg-gray-200 text-black py-3 rounded font-semibold hover:bg-gray-300 transition text-base"
                onClick={handleAddToCart}
                disabled={currentCartQuantity >= 8}
              >
                {currentCartQuantity >= 8 ? "Maximum quantity reached" : "Add to cart"}
              </button>

              {showSuccess && (
                <div className="text-green-600 text-base font-semibold mt-2 text-center">Added to cart successfully!</div>
              )}

              {showError && (
                <div className="text-red-600 text-base font-semibold mt-2 text-center">{errorMessage}</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
