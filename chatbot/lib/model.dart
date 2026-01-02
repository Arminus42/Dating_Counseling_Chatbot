import 'package:flutter/material.dart';

const String baseUrl = "http://127.0.0.1:8000"; 

class ChatMessage {
  final String text;
  final bool isUser;
  final String timestamp;
  final String senderName;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.senderName,
    String? timestamp,
  }) : timestamp = timestamp ?? _getCurrentTime();

  static String _getCurrentTime() {
    final now = DateTime.now();
    final hour = now.hour > 12 ? now.hour - 12 : (now.hour == 0 ? 12 : now.hour);
    final amPm = now.hour >= 12 ? "오후" : "오전";
    final minute = now.minute.toString().padLeft(2, '0');
    return "$amPm $hour:$minute";
  }
}

// [신규] 채팅방의 상태(코치, 성별, 대화내용)를 저장하는 클래스
class ChatRoom {
  final String id;        // 고유 ID (현재는 timestamp 등으로 대체 가능)
  final String title;     // 방 제목 (예: 유재석 코치 - 새 상담 1)
  final String coachName; // 선택된 코치
  final String userGender;// 설정된 성별
  final List<ChatMessage> messages; // 대화 기록 저장소

  ChatRoom({
    required this.id,
    required this.title,
    required this.coachName,
    required this.userGender,
    List<ChatMessage>? messages,
  }) : messages = messages ?? [];
}

const Map<String, String> coachImages = {
  "유재석": "assets/characters/jaesuck.jpg",
  "박명수": "assets/characters/myeongsoo.jpg",
  "하하": "assets/characters/haha.jpg",
  "노홍철": "assets/characters/hongchul.jpg",
  "정준하": "assets/characters/junha.jpg",
  "정형돈": "assets/characters/hyeongdon.jpg",
};

final List<String> characterList = coachImages.keys.toList();

const Color kakaoBg = Color(0xFFBACEE0);
const Color kakaoYellow = Color(0xFFFEE500);
const Color myBubbleText = Colors.black;
const Color coachBubbleText = Colors.black;

