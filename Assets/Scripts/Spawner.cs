using UnityEngine;

public class Spawner : MonoBehaviour
{
    [SerializeField] private GameObject objectToSpawn;
    [SerializeField] private float spawnInterval = 1f;
    [SerializeField] private float xLimit = 8f;

    private float timer;

    private void Update()
    {
        if (GameManager.Instance.IsGameOver) return;

        timer += Time.deltaTime;

        if (timer >= spawnInterval)
        {
            SpawnObject();
            timer = 0f;
        }
    }

    private void SpawnObject()
    {
        float randomX = Random.Range(-xLimit, xLimit);
        Vector3 spawnPos = new Vector3(randomX, transform.position.y, 0f);
        Instantiate(objectToSpawn, spawnPos, Quaternion.identity);
    }
}
