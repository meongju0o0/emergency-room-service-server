import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:dotenv/dotenv.dart';
import 'package:postgres/postgres.dart';

import '../utils/init_user_tables.dart';

// JWT 인증 미들웨어
Middleware authMiddleware() {
  return (handler) {
    return (context) async {
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

        final token = authHeader.substring(7);
        final jwt = JWT.verify(token, SecretKey(secretKey));
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

// 미들웨어 체인 설정
Handler middleware(Handler handler) {
  initializeDatabase();

  return handler
    .use(provider<Connection>((context) => connection))
    .use(authMiddleware());
}
