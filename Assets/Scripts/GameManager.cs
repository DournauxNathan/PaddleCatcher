using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Settings")]
    [SerializeField] private int maxLives = 3;

    [Header("UI")]
    [SerializeField] private TextMeshProUGUI scoreText;
    [SerializeField] private TextMeshProUGUI livesText;
    [SerializeField] private GameObject gameOverPanel;

    public int Score { get; private set; }
    public int Lives { get; private set; }
    public bool IsGameOver { get; private set; }

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

    private void Start()
    {
        Lives = maxLives;
        Score = 0;
        IsGameOver = false;
        UpdateUI();
        if (gameOverPanel != null) gameOverPanel.SetActive(false);
    }

    public void AddScore(int amount)
    {
        if (IsGameOver) return;
        Score += amount;
        UpdateUI();
    }

    public void LoseLife()
    {
        if (IsGameOver) return;
        Lives--;
        UpdateUI();

        if (Lives <= 0)
        {
            GameOver();
        }
    }

    private void UpdateUI()
    {
        if (scoreText != null) scoreText.text = $"Score: {Score}";
        if (livesText != null) livesText.text = $"Lives: {Lives}";
    }

    private void GameOver()
    {
        IsGameOver = true;
        if (gameOverPanel != null) gameOverPanel.SetActive(true);
        if (DataRecorder.Instance != null) DataRecorder.Instance.SaveData();
    }

    public void RestartGame()
    {
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}
