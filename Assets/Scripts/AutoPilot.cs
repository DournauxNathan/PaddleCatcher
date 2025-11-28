using UnityEngine;
using System.Linq;

public class AutoPilot : MonoBehaviour
{
    private PaddleController paddleController;
    private float targetX;

    private void Awake()
    {
        paddleController = GetComponent<PaddleController>();
    }

    private void Start()
    {
        Time.timeScale = 20f;
    }

    private void OnDestroy()
    {
        Time.timeScale = 1f;
    }

    private void FixedUpdate()
    {
        // Find the lowest falling object
        GameObject[] balls = GameObject.FindGameObjectsWithTag("FallingObject");
        
        if (balls.Length > 0)
        {
            // Get the one with lowest Y
            var targetBall = balls.OrderBy(b => b.transform.position.y).First();
            targetX = targetBall.transform.position.x;
        }
        else
        {
            // Stay put or go to center
            targetX = transform.position.x;
        }

        // Move towards targetX
        float direction = 0f;
        if (Mathf.Abs(transform.position.x - targetX) > 0.1f)
        {
            direction = Mathf.Sign(targetX - transform.position.x);
        }

        // Override Paddle Input
        paddleController.SetAutoPilotInput(new Vector2(direction, 0));
    }
}
