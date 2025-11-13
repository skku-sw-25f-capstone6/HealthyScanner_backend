class Product {
  final String id; // UUID
  final String? barcode;
  final String name;
  final String? brand;
  final String? category;

  Product({
    required this.id,
    this.barcode,
    required this.name,
    this.brand,
    this.category,
  });

  // sqflite / 서버 둘 다에서 쓸 수 있게 fromMap/toMap
  factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      id: map['id'] as String,
      barcode: map['barcode'] as String?,
      name: map['name'] as String,
      brand: map['brand'] as String?,
      category: map['category'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'barcode': barcode,
      'name': name,
      'brand': brand,
      'category': category,
    };
  }
}
