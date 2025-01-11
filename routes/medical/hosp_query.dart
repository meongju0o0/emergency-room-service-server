import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();

  final jwt = context.read<JWT>();
  final payload = jwt.payload as Map<String, dynamic>;
  final requesterEmail = payload['email'] as String;

  final body = await context.request.json() as Map<String, dynamic>;

  final email = body['email'] as String?;
  final selectedCourses = body['course'] as List<dynamic>?;
  final xPos = body['x_pos'] as double?;
  final yPos = body['y_pos'] as double?;

  if (email == null) {
    return Response.json(
      body: {'error': 'email is required'},
      statusCode: 400,
    );
  }

  if (requesterEmail != email) {
    return Response.json(
      body: {'error': 'Unauthorized to update this user'},
      statusCode: 403,
    );
  }

  try {
    final conditions = selectedCourses
    ?.map((course) => '"dgidIdName" LIKE \'%$course%\'')
    .join(' OR ');

    if (conditions == null || conditions.isEmpty) {
      return Response.json(
        body: {'error': 'course list is required'},
        statusCode: 400,
      );
    }

    final query = '''
      SELECT
        "dutyName", "dgidIdName", "dutyAddr", "dutyMapimg", "dutyTel1",
        ST_X("geom") AS longitude,
        ST_Y("geom") AS latitude,
        ST_Distance(geom, ST_SetSRID(ST_MAkePoint(@x_pos, @y_pos), 4326)) AS "distance"
      FROM erh_info
      WHERE $conditions
      ORDER BY "distance"
      LIMIT 10;
    ''';

    final List<List<dynamic>> result = await db.execute(
      Sql.named(query),
      parameters: {
        'x_pos': xPos,
        'y_pos': yPos,
      },
    );

    final nameList = result.map((row) => row[0] as String).toList();
    final courseList = result.map((row) => row[1] as String).toList();
    final addrList = result.map((row) => row[2] as String).toList();
    final wayList = result.map((row) => row[3] as String).toList();
    final telList = result.map((row) => row[4] as String).toList();
    final xPosList = result.map((row) => row[5] as double).toList();
    final yPosList = result.map((row) => row[6] as double).toList();

    return Response.json(
      body: {
        'hpid_list': nameList,
        'course_list': courseList,
        'addr_list': addrList,
        'map_list': wayList,
        'tel_list': telList,
        'x_pos_list': xPosList,
        'y_pos_list': yPosList,
      },
    );
  } catch(e) {
    return Response.json(
      body: {
        'error': 'Failed to search hospital id: $e',
      },
      statusCode: 500,
    );
  }
}
