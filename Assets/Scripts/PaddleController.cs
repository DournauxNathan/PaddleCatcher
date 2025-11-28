using UnityEngine;
using UnityEngine;
using UnityEngine.InputSystem;
using System.Runtime.InteropServices;
using System;
using System.Linq;

public class PaddleController : MonoBehaviour
{
    [SerializeField] private float speed = 10f;
    [SerializeField] private float xLimit = 8f;
    [SerializeField] private bool useAI = true;
    [SerializeField] private string modelPath = "Assets/model.txt";

    private Vector2 moveInput;
    public Vector2 MoveInput => moveInput;
    private Rigidbody2D rb;
    
    // AutoPilot Override
    private Vector2 autoPilotInput;
    private bool isAutoPilotActive = false;

    // FFI
    [DllImport("rust_machine_learning_library")]
    private static extern IntPtr mlp_load(string filepath);

    [DllImport("rust_machine_learning_library")]
    private static extern void mlp_predict(IntPtr ptr, float[] inputs, int len_inputs, bool is_classification, float[] outputs, int len_outputs);

    [DllImport("rust_machine_learning_library")]
    private static extern void mlp_free(IntPtr ptr);

    private IntPtr model = IntPtr.Zero;
    private float[] inputBuffer;
    private float[] outputBuffer;
    private const int MAX_BALLS = 3;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Start()
    {
        if (useAI)
        {
            string fullPath = System.IO.Path.GetFullPath(modelPath);
            Debug.Log($"Loading model from: {fullPath}");
            model = mlp_load(fullPath);
            if (model == IntPtr.Zero)
            {
                Debug.LogError("Failed to load ML model!");
                useAI = false;
            }
            else
            {
                // Input size: 1 (PaddleX) + 2 * MAX_BALLS
                inputBuffer = new float[1 + 2 * MAX_BALLS];
                outputBuffer = new float[1]; // Classification output is 1 float (-1 or 1)
            }
        }
    }

    private void OnDestroy()
    {
        if (model != IntPtr.Zero)
        {
            mlp_free(model);
            model = IntPtr.Zero;
        }
    }

    private void FixedUpdate()
    {
        if (isAutoPilotActive)
        {
            moveInput = autoPilotInput;
            isAutoPilotActive = false; // Reset for next frame
        }
        else if (useAI && model != IntPtr.Zero)
        {
            UpdateAI();
        }
        Move();
    }

    public void SetAutoPilotInput(Vector2 input)
    {
        autoPilotInput = input;
        isAutoPilotActive = true;
    }

    private void UpdateAI()
    {
        // 1. Gather Inputs
        inputBuffer[0] = transform.position.x;

        // Find balls
        GameObject[] balls = GameObject.FindGameObjectsWithTag("FallingObject"); // Assuming tag is FallingObject
        
        // Sort by Y (lowest first)
        var sortedBalls = balls.Select(b => b.transform.position).OrderBy(p => p.y).ToList();

        for (int i = 0; i < MAX_BALLS; i++)
        {
            if (i < sortedBalls.Count)
            {
                inputBuffer[1 + i * 2] = sortedBalls[i].x;
                inputBuffer[1 + i * 2 + 1] = sortedBalls[i].y;
            }
            else
            {
                inputBuffer[1 + i * 2] = 0.0f; // Padding X
                inputBuffer[1 + i * 2 + 1] = 10.0f; // Padding Y (far away)
            }
        }

        // 2. Predict
        // is_classification = true (we trained a classification model)
        mlp_predict(model, inputBuffer, inputBuffer.Length, true, outputBuffer, outputBuffer.Length);

        // 3. Act
        float prediction = outputBuffer[0];
        // Prediction is 1.0 (Right) or -1.0 (Left)
        // We can smooth it or just use it directly.
        moveInput = new Vector2(prediction, 0);
    }

    public void OnMove(InputValue value)
    {
        moveInput = value.Get<Vector2>();
    }

    private void Move()
    {
        Vector2 velocity = new Vector2(moveInput.x * speed, rb.linearVelocity.y);
        rb.linearVelocity = velocity;

        // Clamp position
        float clampedX = Mathf.Clamp(transform.position.x, -xLimit, xLimit);
        transform.position = new Vector3(clampedX, transform.position.y, transform.position.z);
    }
}
