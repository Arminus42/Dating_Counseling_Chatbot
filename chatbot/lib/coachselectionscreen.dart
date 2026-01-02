import 'package:chatbot/chatbot.dart';
import 'package:chatbot/model.dart';
import 'package:flutter/material.dart';


// --- 2. 메인 화면 (코치 선택 & 사이드바) ---

class CoachSelectionScreen extends StatefulWidget {
  const CoachSelectionScreen({super.key});

  @override
  State<CoachSelectionScreen> createState() => _CoachSelectionScreenState();
}

class _CoachSelectionScreenState extends State<CoachSelectionScreen> {
  String _selectedGender = "남성";
  final List<String> _genderOptions = ["남성", "여성"];

  // [수정] 단순 String이 아닌 ChatRoom 객체 리스트로 관리
  final List<ChatRoom> _chatRooms = [];
  
  // 현재 선택된 방 인덱스 (-1은 선택 안됨)
  int _selectedRoomIndex = -1; 

  @override
  Widget build(BuildContext context) {
    final double screenWidth = MediaQuery.of(context).size.width;
    final bool isWideScreen = screenWidth > 800;
    final int crossAxisCount = screenWidth > 1000 ? 3 : 2;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text("상담 코치 선택", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
      ),
      drawer: isWideScreen ? null : Drawer(child: _buildSidebarContent()),
      body: SafeArea(
        child: Row(
          children: [
            // 사이드바
            if (isWideScreen)
              SizedBox(
                width: 250,
                child: Container(
                  child: _buildSidebarContent(),
                ),
              ),

            // 메인 콘텐츠
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 900),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 성별 선택
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              "사용자 성별",
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Row(
                              children: _genderOptions.map((gender) {
                                return Padding(
                                  padding: const EdgeInsets.only(left: 10.0),
                                  child: ChoiceChip(
                                    label: Text(gender),
                                    selected: _selectedGender == gender,
                                    selectedColor: kakaoYellow,
                                    backgroundColor: Colors.grey[100],
                                    onSelected: (bool selected) {
                                      setState(() {
                                        _selectedGender = gender;
                                      });
                                    },
                                  ),
                                );
                              }).toList(),
                            ),
                          ],
                        ),
                      ),
                      const Divider(thickness: 1, height: 1),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20, 15, 20, 5),
                        child: const Text(
                          "새로운 상담을 시작할 코치를 선택하세요",
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Expanded(
                        child: GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: crossAxisCount,
                            childAspectRatio: 1.35,
                            crossAxisSpacing: 12,
                            mainAxisSpacing: 12,
                          ),
                          itemCount: characterList.length,
                          itemBuilder: (context, index) {
                            final coachName = characterList[index];
                            final imagePath = coachImages[coachName];

                            return GestureDetector(
                              onTap: () {
                                _createNewChatAndNavigate(coachName);
                              },
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.grey[50],
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: Colors.grey[200]!),
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Container(
                                      width: 140, height: 140,
                                      decoration: const BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Colors.white,
                                      ),
                                      child: ClipOval(
                                        child: imagePath != null
                                            ? Image.asset(imagePath, fit: BoxFit.cover)
                                            : const Icon(Icons.person, size: 80, color: Colors.grey),
                                      ),
                                    ),
                                    const SizedBox(height: 10),
                                    Text(
                                      coachName,
                                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // [기능 1] 새 채팅방 생성 및 입장
  void _createNewChatAndNavigate(String coachName) {
    final newRoom = ChatRoom(
      id: DateTime.now().toString(), // 임시 ID
      title: "$coachName 코치 - 상담 ${_chatRooms.length + 1}",
      coachName: coachName,
      userGender: _selectedGender,
    );

    setState(() {
      _chatRooms.insert(0, newRoom); // 목록 맨 앞에 추가
      _selectedRoomIndex = 0;
    });

    _navigateToChatScreen(newRoom);
  }

  // [기능 2] 기존 채팅방 입장 (사이드바 클릭 시)
  void _enterExistingChat(int index) {
    setState(() {
      _selectedRoomIndex = index;
    });
    
    // 선택된 방의 객체를 가져와서 이동
    _navigateToChatScreen(_chatRooms[index]);
  }

  // 화면 이동 공통 함수
  void _navigateToChatScreen(ChatRoom room) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MbtiChatScreen(chatRoom: room), // 객체 전달
      ),
    ).then((_) {
      // 채팅방에서 나왔을 때(Pop) 화면 갱신 (마지막 대화 내용 등을 반영하고 싶다면)
      setState(() {}); 
    });
  }

  Widget _buildSidebarContent() {
    return Column(
      children: [
        Container(
          height: 100,
          color: Colors.grey[100],
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          alignment: Alignment.bottomLeft,
          child: const Text(
            "내 채팅방 목록",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
        ),
        Expanded(
          child: _chatRooms.isEmpty 
          ? const Center(child: Text("생성된 채팅방이 없습니다.", style: TextStyle(color: Colors.grey)))
          : ListView.separated(
            padding: EdgeInsets.zero,
            itemCount: _chatRooms.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final room = _chatRooms[index];
              final bool isSelected = index == _selectedRoomIndex;
              
              return ListTile(
                title: Text(
                  room.title,
                  style: TextStyle(
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: isSelected ? Colors.black : Colors.grey[700],
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                subtitle: Text(
                  room.messages.isNotEmpty 
                    ? room.messages.last.text // 마지막 메시지 미리보기
                    : "대화 시작 전",
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                ),
                leading: CircleAvatar(
                  backgroundColor: Colors.transparent,
                  backgroundImage: coachImages[room.coachName] != null 
                      ? AssetImage(coachImages[room.coachName]!) 
                      : null,
                  child: coachImages[room.coachName] == null 
                      ? const Icon(Icons.person, color: Colors.grey) 
                      : null,
                ),
                selected: isSelected,
                selectedTileColor: kakaoYellow.withOpacity(0.1),
                onTap: () {
                  // [핵심] 사이드바 클릭 시 해당 채팅방으로 이동
                  _enterExistingChat(index);
                  
                  if (Scaffold.of(context).hasDrawer && Scaffold.of(context).isDrawerOpen) {
                    Navigator.pop(context);
                  }
                },
              );
            },
          ),
        ),
      ],
    );
  }
}


// --- 3. 채팅 화면 (수정됨) ---
