using UnityEngine;

public class FallingObject : MonoBehaviour
{
    [SerializeField] private int scoreValue = 10;
    [SerializeField] private float fallSpeed = 5f;

    private void Start()
    {
        if (DataRecorder.Instance != null)
        {
            DataRecorder.Instance.RegisterBall(this);
        }
    }

    private void OnDestroy()
    {
        if (DataRecorder.Instance != null)
        {
            DataRecorder.Instance.DeregisterBall(this);
        }
    }

    private void Update()
    {
        transform.Translate(Vector3.down * fallSpeed * Time.deltaTime);

        // Destroy if falls below screen
        if (transform.position.y < -10f)
        {
            GameManager.Instance.LoseLife();
            Destroy(gameObject);
        }
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            GameManager.Instance.AddScore(scoreValue);
            Destroy(gameObject);
        }
    }
}
