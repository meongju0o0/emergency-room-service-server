import 'package:postgres/postgres.dart';

/// 전역으로 선언된 PostgreSQL Connection
late final Connection connection;

Future<void> initializeDatabase() async {
  try {
    // 전역 connection에 직접 할당
    connection = await Connection.open(
      Endpoint(
        host: 'localhost',
        database: 'ERSI',
        username: 'postgres',
        password: 'apdpfhd3!',
      ),
      settings: const ConnectionSettings(
        sslMode: SslMode.disable,
      ),
    );

    // 테이블 생성
    await connection.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
      );
    ''');
    await connection.execute('''
      CREATE TABLE IF NOT EXISTS user_disease (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id),
        code TEXT NOT NULL
      );
    ''');
    await connection.execute('''
      CREATE TABLE IF NOT EXISTS user_drug (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id),
        item_seq TEXT NOT NULL
      );
    ''');
    // ignore: lines_longer_than_80_chars
    await connection.execute('CREATE INDEX IF NOT EXISTS idx_email ON users (email);');
    // ignore: lines_longer_than_80_chars
    await connection.execute('CREATE INDEX IF NOT EXISTS idx_user_disease_id ON user_disease (user_id);');
    // ignore: lines_longer_than_80_chars
    await connection.execute('CREATE INDEX IF NOT EXISTS idx_user_drug_id ON user_drug (user_id);');
  } catch (e) {
    rethrow;
  }
}
