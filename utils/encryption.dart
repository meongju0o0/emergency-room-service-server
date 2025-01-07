import 'package:bcrypt/bcrypt.dart';

// 비밀번호 해싱
String hashPassword(String password) {
  return BCrypt.hashpw(password, BCrypt.gensalt());
}

// 비밀번호 검증
bool verifyPassword(String password, String hashedPassword) {
  return BCrypt.checkpw(password, hashedPassword);
}
