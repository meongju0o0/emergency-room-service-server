// ignore_for_file: lines_longer_than_80_chars
import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  // 1) DB와 JWT 주입
  final db = context.read<Connection>();
  final jwt = context.read<JWT>();

  // 2) JWT에서 사용자 정보(email) 추출
  final payload = jwt.payload as Map<String, dynamic>;
  final requesterEmail = payload['email'] as String?;

  if (requesterEmail == null) {
    return Response.json(
      body: {'error': 'Invalid token payload: missing email'},
      statusCode: 400,
    );
  }

  try {
    // 3) DB에서 사용자 정보 조회
    final userResult = await db.execute(Sql.named(
      '''
      SELECT id, username, email
      FROM users
      WHERE email = @email
      '''),
      parameters: {'email': requesterEmail},
    );

    if (userResult.isEmpty) {
      return Response.json(
        body: {'error': 'User not found'},
        statusCode: 404,
      );
    }

    final userRow = userResult.first;
    final userId = userRow[0];
    final username = userRow[1] as String?;
    final email = userRow[2] as String?;

    // 4) 질병 목록(user_disease) 조회
    final diseaseResult = await db.execute(Sql.named(
      '''
      SELECT code
      FROM user_disease
      WHERE user_id = @user_id
      '''),
      parameters: {'user_id': userId},
    );
    final diseaseCodes = diseaseResult.map((row) => row[0]! as String).toList();

    // 5) 복용 중인 약(user_drug) 조회
    final drugResult = await db.execute(Sql.named(
      '''
      SELECT item_seq
      FROM user_drug
      WHERE user_id = @user_id
      '''),
      parameters: {'user_id': userId},
    );
    final medicineCodes = drugResult.map((row) => row[0]! as String).toList();

    // 6) 응답 JSON 생성
    final responseBody = {
      'id': userId,
      'email': email,
      'username': username,
      'disease_codes': diseaseCodes,
      'medicine_codes': medicineCodes,
    };

    return Response.json(body: responseBody);
  } catch (e) {
    return Response.json(
      body: {
        'error': 'Failed to fetch user info: $e',
      },
      statusCode: 500,
    );
  }
}
