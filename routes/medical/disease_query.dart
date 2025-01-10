import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';

Future<Response> onRequest(RequestContext context) async {
  return Response.json(
    body: {'error': 'API Not Implemented Yet'},
    statusCode: 404,
  );
}
