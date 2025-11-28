using UnityEngine;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Linq;

public class DataRecorder : MonoBehaviour
{
    public static DataRecorder Instance { get; private set; }

    private List<FallingObject> activeBalls = new List<FallingObject>();
    private List<string> recordedFrames = new List<string>();
    
    [SerializeField] private PaddleController paddle;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void OnApplicationQuit()
    {
        SaveData();
    }

    private void FixedUpdate()
    {
        if (GameManager.Instance.IsGameOver) return;
        if (paddle == null) return;

        RecordFrame();
    }

    public void RegisterBall(FallingObject ball)
    {
        if (!activeBalls.Contains(ball))
        {
            activeBalls.Add(ball);
        }
    }

    public void DeregisterBall(FallingObject ball)
    {
        if (activeBalls.Contains(ball))
        {
            activeBalls.Remove(ball);
        }
    }

    private void RecordFrame()
    {
        float paddleX = paddle.transform.position.x;
        float actionX = paddle.MoveInput.x;
        
        // Format balls as x:y|x:y
        List<string> ballPositions = new List<string>();
        foreach (var ball in activeBalls)
        {
            if (ball != null)
            {
                ballPositions.Add($"{ball.transform.position.x.ToString(System.Globalization.CultureInfo.InvariantCulture)}:{ball.transform.position.y.ToString(System.Globalization.CultureInfo.InvariantCulture)}");
            }
        }
        string ballsData = string.Join("|", ballPositions);

        // CSV Line: PaddleX,ActionX,BallsData
        string csvLine = $"{paddleX.ToString(System.Globalization.CultureInfo.InvariantCulture)},{actionX.ToString(System.Globalization.CultureInfo.InvariantCulture)},{ballsData}";
        recordedFrames.Add(csvLine);
    }

    public void SaveData()
    {
        string path = Path.Combine(Application.dataPath, "../perfect_dataset.csv");
        bool fileExists = File.Exists(path);

        StringBuilder sb = new StringBuilder();
        
        // Add header if file doesn't exist
        if (!fileExists)
        {
            sb.AppendLine("PaddleX,ActionX,BallsData");
        }

        foreach (string frame in recordedFrames)
        {
            sb.AppendLine(frame);
        }

        // Append to file
        File.AppendAllText(path, sb.ToString());
        
        Debug.Log($"Saved {recordedFrames.Count} frames to {path}");
        recordedFrames.Clear();
    }
}
