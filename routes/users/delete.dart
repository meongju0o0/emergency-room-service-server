import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();

  // JWT에서 사용자 정보 추출
  final jwt = context.read<JWT>();
  final payload = jwt.payload as Map<String, dynamic>;
  final requesterEmail = payload['email'] as String;

  final body = await context.request.json() as Map<String, dynamic>;
  final email = body['email'] as String?;

  if (email == null) {
    return Response.json(
      body: {'error': 'email is required'},
      statusCode: 400,
    );
  }

  try {
    // 요청자가 본인인지 확인
    if (requesterEmail != email) {
      return Response.json(
        body: {'error': 'Unauthorized to delete this user'},
        statusCode: 403,
      );
    }

    // 사용자 ID 가져오기
    final result = await db.execute(
      Sql.named('SELECT id FROM users WHERE email = @email'),
      parameters: {
        'email': email,
      },
    );

    if (result.isEmpty) {
      return Response.json(
        body: {'error': 'User not found'},
        statusCode: 404,
      );
    }

    final userId = result.first[0];

    // 질병 코드 삭제
    await db.execute(
      Sql.named('DELETE FROM user_disease WHERE user_id = @user_id'),
      parameters: {
        'user_id': userId,
        },
    );

    // 의약품 코드 삭제
    await db.execute(
      Sql.named('DELETE FROM user_drug WHERE user_id = @user_id'),
      parameters: {
        'user_id': userId,
        },
    );

    // 사용자 삭제
    await db.execute(
      Sql.named('DELETE FROM users WHERE id = @user_id'),
      parameters: {
        'user_id': userId,
        },
    );

    return Response.json(
      body: {'message': 'User deleted successfully'},
    );
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to delete user: $e'},
      statusCode: 500,
    );
  }
}
