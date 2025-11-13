import 'package:sqflite/sqflite.dart';
import '../../models/product.dart';

class ProductLocalDataSource {
  final Database db;

  ProductLocalDataSource(this.db);

  Future<Product?> getByProductId(String productId) async {
    final rows = await db.query(
      'product',
      where: 'barcode = ?',
      whereArgs: [productId],
      limit: 1,
    );
    if (rows.isEmpty) return null;
    return Product.fromMap(rows.first);
  }

  Future<void> upsert(Product product) async {
    await db.insert(
      'product',
      product.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }
}
