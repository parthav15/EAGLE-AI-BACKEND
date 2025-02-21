import cv2
import torch
from torch import amp
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Camera, DetectionLog, Alert

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

danger_objects = ['knife', 'gun', 'scissors', 'fire', 'explosive', 'hammer', 'screwdriver', 'razor', 'sword', 'axe']

from django.views.decorators.http import require_http_methods
from .models import Camera
from users.models import CustomUser
import json

from users.utils import jwt_encode, jwt_decode, auth_user

@csrf_exempt
@require_http_methods(["GET"])
def list_cameras(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        cameras = Camera.objects.filter(user=user)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error fetching cameras: {str(e)}'}, status=500)
    
    camera_list = [
        {
            "id": camera.id,
            "name": camera.name,
            "ip_url": camera.ip_url,
            "is_active": camera.is_active
        }
        for camera in cameras
    ]
    return JsonResponse(
        {
            "success": True,
            "message": "Cameras fetched successfully",
            "cameras": camera_list
        },
        status=200
    )

@csrf_exempt
@require_http_methods(["GET"])
def get_camera(request, camera_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        user = CustomUser.objects.get(email=user_email)
        camera = Camera.objects.get(id=camera_id, user=user)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    except Camera.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Camera not found.'}, status=404)
    
    camera_data = {
        "id": camera.id,
        "name": camera.name,
        "ip_url": camera.ip_url,
        "is_active": camera.is_active
    }
    return JsonResponse(
        {
            "success": True,
            "message": "Camera fetched successfully",
            "camera": camera_data
        },
        status=200
    )

@csrf_exempt
@require_http_methods(["POST"])
def add_camera(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    try:
        camera = Camera.objects.create(
            user=user,
            name=data.get('name'),
            ip_url=data.get('ip_url'),
            is_active=data.get('is_active', True)
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating camera: {str(e)}'}, status=500)
    
    return JsonResponse(
        {
            "success": True,
            "message": "Camera added successfully",
            "camera": {
                "id": camera.id,
                "name": camera.name,
                "ip_url": camera.ip_url,
                "is_active": camera.is_active
            }
        },
        status=201
    )

@csrf_exempt
@require_http_methods(["PUT"])
def update_camera(request, camera_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        user = CustomUser.objects.get(email=user_email)
        camera = Camera.objects.get(id=camera_id, user=user)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    except Camera.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Camera not found.'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    if 'name' in data:
        camera.name = data.get('name')
    if 'ip_url' in data:
        camera.ip_url = data.get('ip_url')
    if 'is_active' in data:
        camera.is_active = data.get('is_active')
    
    camera.save()
    return JsonResponse(
        {
            "success": True,
            "message": "Camera updated successfully",
            "camera": {
                "id": camera.id,
                "name": camera.name,
                "ip_url": camera.ip_url,
                "is_active": camera.is_active
            }
        },
        status=200
    )

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_camera(request, camera_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')
    
    try:
        user = CustomUser.objects.get(email=user_email)
        camera = Camera.objects.get(id=camera_id, user=user)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    except Camera.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Camera not found.'}, status=404)
    
    camera.delete()
    return JsonResponse({"success": True, "message": "Camera deleted successfully"}, status=200)


def generate_frames(camera_url):
    cap = cv2.VideoCapture(camera_url)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        with amp.autocast('cuda'):
            results = model(frame)
        
        detections = results.pandas().xyxy[0]

        for _, row in detections.iterrows():
            x1, y1, x2, y2, confidence, cls = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']), row['confidence'], row['name']
            
            if confidence > 0.4 and cls in danger_objects:
                detection_log = DetectionLog.objects.create(
                    camera=Camera.objects.get(ip_url=camera_url),
                    object_type=cls,
                    confidence=confidence,
                    x_min=x1,
                    y_min=y1,
                    x_max=x2,
                    y_max=y2
                )
                Alert.objects.create(
                    camera=detection_log.camera,
                    detection_log=detection_log,
                    message=f"Danger: {cls} {confidence:.2f}"
                )
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"Danger: {cls} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{cls} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@csrf_exempt
def video_stream(request):
    camera_url = request.GET.get('camera_url')
    return StreamingHttpResponse(generate_frames(camera_url), content_type='multipart/x-mixed-replace; boundary=frame')

# @csrf_exempt
# def video_stream(request):
#     cameras = Camera.objects.all()
#     frames = (frame for camera in cameras for frame in generate_frames(camera.ip_url))
#     return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')