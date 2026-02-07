import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter_app/state/chat_state.dart';
import 'package:flutter_app/api/client.dart';
import 'package:flutter_app/widgets/personality_selector.dart';

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ApiClient _api = ApiClient();
  String userId = Uuid().v4();
  String _selectedTone = "supportive";
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    // optionally load saved user id from persistent storage later
  }

  void _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _controller.clear();

    final chatState = Provider.of<ChatState>(context, listen: false);
    final userMsg = ChatMessage(id: Uuid().v4(), from: 'user', text: text);
    chatState.addMessage(userMsg);

    setState(() {
      _loading = true;
    });

    try {
      final result = await _api.sendChat(
        userId: userId,
        message: text,
        personality: _selectedTone,
      );

      // response handling: standard format from backend:
      // { "agent_used": "...", "response": {...}, "tone": "supportive", ... }
      String replyText;
      if (result.containsKey('response')) {
        final resp = result['response'];
        if (resp is Map && resp.containsKey('response')) {
          replyText = resp['response'].toString();
        } else {
          replyText = resp.toString();
        }
      } else {
        replyText = result.toString();
      }

      final agentMsg = ChatMessage(
        id: Uuid().v4(),
        from: 'agent',
        text: replyText,
      );
      chatState.addMessage(agentMsg);
    } catch (e) {
      final chatState = Provider.of<ChatState>(context, listen: false);
      chatState.addMessage(
        ChatMessage(id: Uuid().v4(), from: 'agent', text: 'Error: $e'),
      );
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Widget _buildMessage(ChatMessage m) {
    final isUser = m.from == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 6, horizontal: 12),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser ? Colors.indigo[100] : Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(m.text),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final chatState = Provider.of<ChatState>(context);
    return Scaffold(
      appBar: AppBar(
        title: Text('Finance Agent'),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: PersonalitySelector(
              selected: _selectedTone,
              onChanged: (val) => setState(() => _selectedTone = val),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: chatState.messages.length,
              itemBuilder: (ctx, i) => _buildMessage(chatState.messages[i]),
            ),
          ),
          if (_loading) LinearProgressIndicator(),
          SafeArea(
            child: Row(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(left: 12.0, right: 8.0),
                    child: TextField(
                      controller: _controller,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      decoration: InputDecoration(
                        hintText: 'Ask about spending, budgets, investing...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ),
                IconButton(icon: Icon(Icons.send), onPressed: _send),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
