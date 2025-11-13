import '../data/local/product_local_data_source.dart';
import '../data/remote/product_remote_data_source.dart';
import '../models/product.dart';

class ProductRepository {
  final ProductLocalDataSource local;
  final ProductRemoteDataSource remote;

  ProductRepository({
    required this.local,
    required this.remote,
  });

  /// 바코드로 상품 조회:
  /// 1) 로컬 캐시 먼저 조회
  /// 2) 없으면 서버에서 조회 후 로컬에 저장
  Future<Product?> getByBarcode(String barcode) async {
    // 1) 로컬 캐시 조회
    final cached = await local.getByProductId(barcode);
    if (cached != null) {
      return cached;
    }

    // 2) 서버 조회
    final fetched = await remote.fetchByProductId(barcode);
    if (fetched != null) {
      // 3) 로컬에 캐시
      await local.upsert(fetched);
    }
    return fetched;
  }
}
