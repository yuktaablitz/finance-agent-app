import 'package:flutter/foundation.dart';

class ChatMessage {
  final String id;
  final String from; // 'user' or 'agent'
  final String text;
  ChatMessage({required this.id, required this.from, required this.text});
}

class ChatState extends ChangeNotifier {
  List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => List.unmodifiable(_messages);

  void addMessage(ChatMessage m) {
    _messages.add(m);
    notifyListeners();
  }

  void setMessages(List<ChatMessage> list) {
    _messages = list;
    notifyListeners();
  }

  void clear() {
    _messages = [];
    notifyListeners();
  }
}
