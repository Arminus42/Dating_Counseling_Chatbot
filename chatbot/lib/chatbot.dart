
import 'dart:convert';

import 'package:chatbot/model.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// --- 설정 ---
const String baseUrl = "http://127.0.0.1:8000"; 
// ----------------

class MbtiChatScreen extends StatefulWidget {
  final ChatRoom chatRoom; 

  const MbtiChatScreen({
    super.key,
    required this.chatRoom,
  });

  @override
  State<MbtiChatScreen> createState() => _MbtiChatScreenState();
}

class _MbtiChatScreenState extends State<MbtiChatScreen> {
  late String currentCoach;
  String? sessionId;

  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  List<ChatMessage> messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    currentCoach = widget.chatRoom.coachName;
    messages = widget.chatRoom.messages; 

    if (messages.isEmpty) {
      _sendGreetingMessage();
    } else {
      WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
    }
  }

  void _sendGreetingMessage() {
    String greeting = "";
    
    switch (currentCoach) {
      case "유재석":
        greeting = "안녕하세요~ 많이 기다리셨죠? 고민 상담하고 싶으신 거군요! 무슨 일인지 편하게 말씀해 주시면 제가 정말 제 일처럼 열심히 고민 상담 해드릴게요. 자, 말씀해 보세요!";
        break;
      case "박명수":
        greeting = "뭔데. 말해봐. 길게 말하지 말고 딱 핵심만 말해. 나 바빠.";
        break;
      case "정준하":
        greeting = "어우~ 연애가 고민이야? 그 마음 내가 잘 알지... 그럼 제가 우리 니모 생각하는 마음으로 열~씸히! 답변 해드릴게요. 말씀해 봐요~";
        break;
      case "노홍철":
        greeting = "미쳤어 미쳤어! 연애 고민이라니! 이건 정말 대박 사건이야! 어쩔 거야~ 어쩔 거야~! 하지만 걱정 마! 일단 긍정!!! 긍정!!! 웃으면 복이 오고 행복해진다니까?! 자, 가는 거야~!";
        break;
      case "하하":
        greeting = "오... 연애 고민...? (눈치 보며) 사실 저도 잘 모르겠어욤... 그래도 친구로서 같이 고민은 해줄게! 리얼하게 말해봐, 야만!";
        break;
      case "정형돈":
        greeting = "(하품을 크게 하며) 아... 예... 무슨 고민이 있을까요? 제가 뭐 딱히 드릴 말씀은 없지만... 일단 한 번 들어나 봅시다. 짧게 좀 해줘요.";
        break;
      default:
        greeting = "안녕? 난 $currentCoach 코치야. 고민을 말해봐.";
    }

    _addMessage(ChatMessage(
      text: greeting,
      isUser: false,
      senderName: "$currentCoach 코치",
    ));
  }

  void _addMessage(ChatMessage message) {
    setState(() {
      if (!widget.chatRoom.messages.contains(message)) {
         widget.chatRoom.messages.add(message);
      }
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  // [수정됨] 로그 출력 기능 추가
  Future<void> _sendMessageToBackend(String userText) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final url = Uri.parse("$baseUrl/chat");

      final body = jsonEncode({
        "session_id": sessionId,
        "user_gender": widget.chatRoom.userGender,
        "character": currentCoach,
        "message": userText,
      });

      // 🔵 [Log] 요청 로그 (보내는 데이터)
      print("\n============== [REQUEST] ==============");
      print("URL: $url");
      print("BODY: $body");
      print("=======================================\n");

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: body,
      );

      // 한글 깨짐 방지를 위해 미리 디코딩
      final decodedResponse = utf8.decode(response.bodyBytes);

      // 🟢 [Log] 응답 로그 (받은 데이터)
      print("\n============== [RESPONSE] ==============");
      print("STATUS: ${response.statusCode}");
      print("BODY: $decodedResponse");
      print("========================================\n");

      if (response.statusCode == 200) {
        final responseData = jsonDecode(decodedResponse);
        sessionId = responseData['session_id'];
        final aiResponse = responseData['response'];

        _addMessage(ChatMessage(
          text: aiResponse,
          isUser: false,
          senderName: "$currentCoach 코치",
        ));
      } else {
        _addMessage(ChatMessage(
          text: "서버 오류 (Code: ${response.statusCode})",
          isUser: false,
          senderName: "System",
        ));
      }
    } catch (e) {
      // 🔴 [Log] 에러 로그
      print("\n============== [ERROR] ==============");
      print("Message: $e");
      print("=====================================\n");

      _addMessage(ChatMessage(
        text: "서버 연결 실패: $e",
        isUser: false,
        senderName: "System",
      ));
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _handleSend() {
    if (_textController.text.trim().isEmpty) return;
    if (_isLoading) return;

    final userText = _textController.text;
    _textController.clear();

    _addMessage(ChatMessage(
      text: userText,
      isUser: true,
      senderName: "나",
    ));

    _sendMessageToBackend(userText);
  }

  @override
  Widget build(BuildContext context) {
    // 기존 UI 코드 유지
    return Scaffold(
      backgroundColor: const Color(0xFFBACEE0), // kakaoBg
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: Colors.black,
        title: Text(
          "$currentCoach 코치님", 
          style: const TextStyle(fontWeight: FontWeight.bold)
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.separated(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              itemCount: messages.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                return MessageItem(message: messages[index]);
              },
            ),
          ),
          if (_isLoading)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 4),
              color: Colors.white.withOpacity(0.5),
              child: const Center(
                child: Text("답변 생성 중...", style: TextStyle(fontSize: 12, color: Colors.grey)),
              ),
            ),
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildInputBar() {
    const Color kakaoYellow = Color(0xFFFEE500);
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: const Color(0xFFF2F2F2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: TextField(
                controller: _textController,
                minLines: 1,
                maxLines: 4,
                enabled: !_isLoading,
                onChanged: (text) => setState(() {}),
                decoration: const InputDecoration(
                  border: InputBorder.none,
                  hintText: "메시지를 입력하세요",
                  isDense: true,
                  contentPadding: EdgeInsets.symmetric(vertical: 10),
                ),
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              color: _textController.text.isNotEmpty ? kakaoYellow : Colors.grey[300],
              shape: BoxShape.circle,
            ),
            child: IconButton(
              icon: const Icon(Icons.send, size: 20),
              color: _textController.text.isNotEmpty ? Colors.black : Colors.white,
              onPressed: (_textController.text.isNotEmpty && !_isLoading) ? _handleSend : null,
            ),
          ),
        ],
      ),
    );
  }
}
// --- 4. 메시지 아이템 (기존 유지) ---
class MessageItem extends StatelessWidget {
  final ChatMessage message;

  const MessageItem({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    if (message.senderName == "System") {
      return Center(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.5),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            message.text,
            style: const TextStyle(fontSize: 14, color: Colors.grey),
          ),
        ),
      );
    }

    final isUser = message.isUser;

    return Row(
      mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (!isUser) ...[
          Padding(
            padding: const EdgeInsets.only(right: 10.0),
            child: Container(
              width: 60, height: 60,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: ClipOval(
                child: Builder(
                  builder: (context) {
                    final baseName = message.senderName.replaceAll(" 코치", "");
                    final imagePath = coachImages[baseName];
                    if (imagePath != null) {
                      return Image.asset(imagePath, fit: BoxFit.cover, errorBuilder: (c,e,s)=>const Icon(Icons.person));
                    }
                    return Center(child: Text(baseName.isNotEmpty ? baseName.substring(0, 1) : "?"));
                  },
                ),
              ),
            ),
          ),
        ],

        Flexible(
          child: Column(
            crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
            children: [
              if (!isUser)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    message.senderName,
                    style: const TextStyle(fontSize: 30, color: Colors.grey),
                  ),
                ),
              
              Row(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  if (isUser) _buildTimeText(message.timestamp),
                  
                  Flexible(
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      constraints: const BoxConstraints(maxWidth: 980), 
                      decoration: BoxDecoration(
                        color: isUser ? kakaoYellow : Colors.white,
                        borderRadius: BorderRadius.only(
                          topLeft: isUser ? const Radius.circular(20) : Radius.zero,
                          topRight: isUser ? Radius.zero : const Radius.circular(20),
                          bottomLeft: const Radius.circular(20),
                          bottomRight: const Radius.circular(20),
                        ),
                        boxShadow: [
                            BoxShadow(
                             color: Colors.black.withOpacity(0.05),
                             blurRadius: 2,
                             offset: const Offset(0, 2),
                            )
                        ],
                      ),
                      child: Text(
                        message.text,
                        style: TextStyle(
                          fontSize: 26,
                          height: 1.4,
                          color: isUser ? myBubbleText : coachBubbleText,
                        ),
                      ),
                    ),
                  ),

                  if (!isUser) _buildTimeText(message.timestamp),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTimeText(String time) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 6),
      child: Text(
        time,
        style: const TextStyle(fontSize: 14, color: Colors.black54),
      ),
    );
  }
}