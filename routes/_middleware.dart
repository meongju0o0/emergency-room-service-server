import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:dotenv/dotenv.dart';
import 'package:sqlite3/sqlite3.dart';

// 데이터베이스 초기화
final db = sqlite3.open('user_database.db');

Handler middleware(Handler handler) {
  db
    ..execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
      );
    ''')
    ..execute('''
      CREATE TABLE IF NOT EXISTS user_disease (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      );
    ''')
    ..execute('''
      CREATE TABLE IF NOT EXISTS user_medicine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
      );
    ''')
    ..execute('CREATE INDEX IF NOT EXISTS idx_email ON users (email);');

  return handler
      .use(provider<Database>((context) => db)) // DB 핸들러에 등록
      .use(authMiddleware()); // JWT 인증 핸들러에 등록
}

// JWT 인증 미들웨어
Middleware authMiddleware() {
  return (handler) {
    return (context) async {
      // 인증이 필요 없는 경로
      final unprotectedPaths = ['/', '/users/add', '/users/read'];
      if (unprotectedPaths.contains(context.request.uri.path)) {
        return handler(context);
      }

      try {
        final authHeader = context.request.headers['Authorization'];
        if (authHeader == null || !authHeader.startsWith('Bearer ')) {
          return Response.json(
            body: {'error': 'Authorization header is missing'},
            statusCode: 401,
          );
        }

        final dotenv = DotEnv()..load();
        final secretKey = dotenv['JWT_SECRET_KEY'] ?? 'default_secret_key';

        final token = authHeader.substring(7); // "Bearer " 이후의 토큰 추출
        final jwt = JWT.verify(token, SecretKey(secretKey)); // JWT 검증

        // 사용자 정보를 컨텍스트에 저장
        context = context.provide<JWT>(() => jwt);

        return handler(context);
      } catch (e) {
        return Response.json(
          body: {'error': 'Invalid or expired token'},
          statusCode: 401,
        );
      }
    };
  };
}
