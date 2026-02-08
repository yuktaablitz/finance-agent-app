import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:flutter_app/api/client.dart';

class ReceiptUploadScreen extends StatefulWidget {
  final String userId;

  const ReceiptUploadScreen({super.key, required this.userId});

  @override
  _ReceiptUploadScreenState createState() => _ReceiptUploadScreenState();
}

class _ReceiptUploadScreenState extends State<ReceiptUploadScreen> {
  final ApiClient _api = ApiClient();
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  bool _uploading = false;
  Map<String, dynamic>? _extractedTransaction;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(source: source);
      if (image != null) {
        setState(() {
          _selectedImage = File(image.path);
          _extractedTransaction = null;
        });
      }
    } catch (e) {
      _showError('Failed to pick image: $e');
    }
  }

  Future<void> _uploadReceipt() async {
    if (_selectedImage == null) return;

    setState(() {
      _uploading = true;
    });

    try {
      final result = await _api.uploadReceipt(
        userId: widget.userId,
        imagePath: _selectedImage!.path,
      );

      setState(() {
        _extractedTransaction = result['transaction'];
        _uploading = false;
      });

      _showSuccess('Receipt processed successfully!');
    } catch (e) {
      setState(() {
        _uploading = false;
      });
      _showError('Upload failed: $e');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  Widget _buildTransactionCard() {
    if (_extractedTransaction == null) return SizedBox.shrink();

    final tx = _extractedTransaction!;
    return Card(
      margin: EdgeInsets.all(16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Extracted Transaction', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 12),
            _buildField('Merchant', tx['merchant']),
            _buildField('Amount', '\$${tx['amount']?.toStringAsFixed(2) ?? '0.00'}'),
            _buildField('Date', tx['date']),
            _buildField('Category', tx['category']),
            _buildField('Description', tx['description']),
          ],
        ),
      ),
    );
  }

  Widget _buildField(String label, dynamic value) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text('$label:', style: TextStyle(fontWeight: FontWeight.w600)),
          ),
          Expanded(child: Text(value?.toString() ?? 'N/A')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Upload Receipt'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            if (_selectedImage != null)
              Container(
                height: 300,
                width: double.infinity,
                margin: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.file(_selectedImage!, fit: BoxFit.contain),
                ),
              ),
            
            Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton.icon(
                    onPressed: _uploading ? null : () => _pickImage(ImageSource.camera),
                    icon: Icon(Icons.camera_alt),
                    label: Text('Camera'),
                  ),
                  ElevatedButton.icon(
                    onPressed: _uploading ? null : () => _pickImage(ImageSource.gallery),
                    icon: Icon(Icons.photo_library),
                    label: Text('Gallery'),
                  ),
                ],
              ),
            ),

            if (_selectedImage != null)
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _uploading ? null : _uploadReceipt,
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.indigo,
                      foregroundColor: Colors.white,
                    ),
                    child: _uploading
                        ? SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : Text('Process Receipt', style: TextStyle(fontSize: 16)),
                  ),
                ),
              ),

            _buildTransactionCard(),
          ],
        ),
      ),
    );
  }
}
