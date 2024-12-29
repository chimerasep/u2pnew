using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class CameraFrameSender : MonoBehaviour
{
    public Camera mainCamera;
    public Camera secondCamera;
    public GameObject displayObject;
    private RenderTexture secondCameraRenderTexture;
    private RenderTexture captureRT; // Reuse RenderTexture
    private Texture2D captureTexture; // Reuse Texture2D
    private bool isProcessing = false;

    private string serverUrl = "http://127.0.0.1:5000/process-frame";
    private Texture2D currentProcessedTexture;

    [Header("Motion Magnification Settings")]
    public float phaseMagnification = 25.0f;
    public float frequencyLow = 0.2f;
    public float frequencyHigh = 0.25f;
    public float sigma = 2.0f;
    public bool attenuate = false;

    [Header("Performance Settings")]
    [Range(0.1f, 1.0f)]
    public float resolutionScale = 0.5f; // Scale down resolution for better performance
    [Range(1, 100)]
    public int jpegQuality = 50; // Lower quality for better performance

    private void Start()
    {
        secondCameraRenderTexture = secondCamera.targetTexture;
        
        // Create reusable textures
        int width = Mathf.RoundToInt(Screen.width * resolutionScale);
        int height = Mathf.RoundToInt(Screen.height * resolutionScale);
        captureRT = new RenderTexture(width, height, 24);
        captureTexture = new Texture2D(width, height, TextureFormat.RGB24, false);
        
        StartCoroutine(SendFrameCoroutine());
    }

    private void OnDestroy()
    {
        if (currentProcessedTexture != null) Destroy(currentProcessedTexture);
        if (captureRT != null) Destroy(captureRT);
        if (captureTexture != null) Destroy(captureTexture);
    }

    IEnumerator SendFrameCoroutine()
    {
        while (true)
        {
            if (!isProcessing)
            {
                isProcessing = true;
                byte[] frameBytes = CaptureFrame();
                StartCoroutine(SendFrameToServer(frameBytes));
            }
            yield return new WaitForSeconds(1f / 60f); // Increased frame rate
        }
    }

    byte[] CaptureFrame()
    {
        mainCamera.targetTexture = captureRT;
        mainCamera.Render();

        RenderTexture.active = captureRT;
        captureTexture.ReadPixels(new Rect(0, 0, captureRT.width, captureRT.height), 0, 0);
        captureTexture.Apply();

        mainCamera.targetTexture = null;
        RenderTexture.active = null;

        return captureTexture.EncodeToJPG(jpegQuality);
    }

    IEnumerator SendFrameToServer(byte[] frameBytes)
    {
        using (UnityWebRequest www = UnityWebRequest.Put(serverUrl, frameBytes))
        {
            www.method = UnityWebRequest.kHttpVerbPOST;
            www.SetRequestHeader("Content-Type", "application/octet-stream");

            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                OnReceiveProcessedFrame(www.downloadHandler.data);
            }
            else
            {
                Debug.LogError($"Error sending frame: {www.error}");
                Debug.LogError($"Response Code: {www.responseCode}");
                Debug.LogError($"Response Text: {www.downloadHandler.text}");
                
                // Add a small delay before retrying
                yield return new WaitForSeconds(0.1f);
            }
            isProcessing = false;
        }
    }

    void OnReceiveProcessedFrame(byte[] processedBytes)
    {
        if (currentProcessedTexture != null)
        {
            Destroy(currentProcessedTexture);
        }

        currentProcessedTexture = new Texture2D(2, 2);
        currentProcessedTexture.LoadImage(processedBytes);

        if (secondCameraRenderTexture != null)
        {
            Graphics.Blit(currentProcessedTexture, secondCameraRenderTexture);
        }

        if (displayObject != null)
        {
            var renderer = displayObject.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.mainTexture = currentProcessedTexture;
            }
        }
    }
}
