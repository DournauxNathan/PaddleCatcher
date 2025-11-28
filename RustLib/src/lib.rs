use rand::Rng;
use std::slice;
use std::fs::File;
use std::io::{Write, Read, BufReader, BufRead};
use std::ffi::CStr;
use std::os::raw::c_char;

/// PERCEPTRON SIMPLE
pub struct Perceptron {
    poids: Vec<f32>,
    seuil: f32,
    vitesse_apprentissage: f32,
    classification: bool,
}

impl Perceptron {
    pub fn new(nombre_entree: usize, vitesse_apprentissage: f32, classification: bool) -> Self {
        Self {
            poids: vec![0.0; nombre_entree],
            seuil: 0.0,
            vitesse_apprentissage,
            classification,
        }
    }

    pub fn predict(&self, entrees: &[f32]) -> f32 {
        let mut total = self.seuil;
        for (i, &entree) in entrees.iter().enumerate() {
            if i < self.poids.len() {
                total += entree * self.poids[i];
            }
        }
        if self.classification {
            if total >= 0.0 { 1.0 } else { -1.0 }
        } else {
            total
        }
    }

    pub fn train(&mut self, entrees: &[f32], attendu: f32) {
        let prediction = self.predict(entrees);
        let erreur = attendu - prediction;
        for i in 0..self.poids.len() {
            if i < entrees.len() {
                self.poids[i] += self.vitesse_apprentissage * erreur * entrees[i];
            }
        }
        self.seuil += self.vitesse_apprentissage * erreur;
    }
}

// --- FFI Perceptron ---

#[no_mangle]
pub extern "C" fn perceptron_new(input_size: i32, lr: f32, classification: bool) -> *mut Perceptron {
    let p = Perceptron::new(input_size as usize, lr, classification);
    Box::into_raw(Box::new(p))
}

#[no_mangle]
pub extern "C" fn perceptron_predict(ptr: *mut Perceptron, inputs: *const f32, len: i32) -> f32 {
    if ptr.is_null() || inputs.is_null() { return 0.0; }
    let p = unsafe { &*ptr };
    let input_slice = unsafe { slice::from_raw_parts(inputs, len as usize) };
    p.predict(input_slice)
}

#[no_mangle]
pub extern "C" fn perceptron_train(ptr: *mut Perceptron, inputs: *const f32, len: i32, expected: f32) {
    if ptr.is_null() || inputs.is_null() { return; }
    let p = unsafe { &mut *ptr };
    let input_slice = unsafe { slice::from_raw_parts(inputs, len as usize) };
    p.train(input_slice, expected);
}

#[no_mangle]
pub extern "C" fn perceptron_free(ptr: *mut Perceptron) {
    if ptr.is_null() { return; }
    unsafe {
        let _ = Box::from_raw(ptr);
    }
}


/// MLP (Multi-Layer Perceptron)
pub struct MLP {
    d: Vec<usize>,
    l: usize,
    w: Vec<Vec<Vec<f32>>>,
    x: Vec<Vec<f32>>,
    deltas: Vec<Vec<f32>>,
}

impl MLP {
    pub fn new(neurons_per_layer: Vec<usize>) -> Self {
        let mut rng = rand::thread_rng();
        let d = neurons_per_layer.clone();
        let l = d.len().saturating_sub(1);
        let mut w: Vec<Vec<Vec<f32>>> = Vec::with_capacity(d.len());

        for layer in 0..d.len() {
            if layer == 0 { w.push(Vec::new()); continue; }
            let mut layer_w: Vec<Vec<f32>> = Vec::with_capacity(d[layer - 1] + 1);
            for _i in 0..=d[layer - 1] {
                let mut row: Vec<f32> = Vec::with_capacity(d[layer] + 1);
                for j in 0..=d[layer] {
                    if j == 0 { row.push(0.0); } // biais
                    else { row.push(rng.gen::<f32>() * 2.0 - 1.0); }
                }
                layer_w.push(row);
            }
            w.push(layer_w);
        }

        let mut x: Vec<Vec<f32>> = Vec::with_capacity(d.len());
        let mut deltas: Vec<Vec<f32>> = Vec::with_capacity(d.len());
        for &neurons in &d {
            let mut xv = vec![0.0_f32; neurons + 1];
            xv[0] = 1.0; // biais
            let dv = vec![0.0_f32; neurons + 1];
            x.push(xv);
            deltas.push(dv);
        }

        Self { d, l, w, x, deltas }
    }

    fn propagate(&mut self, inputs: &[f32], is_classification: bool) {
        // Safety check
        if inputs.len() != self.d[0] {
            // In production code, handle error. Here we just return or panic.
            // But for FFI, panic is bad. We'll just try to copy what we can.
        }
        
        for (j, &val) in inputs.iter().enumerate() {
            if j + 1 < self.x[0].len() {
                self.x[0][j + 1] = val;
            }
        }

        for layer in 1..=self.l {
            for j in 1..=self.d[layer] {
                let mut signal = 0.0;
                for i in 0..=self.d[layer - 1] {
                    signal += self.w[layer][i][j] * self.x[layer - 1][i];
                }
                let val = if is_classification || layer != self.l { signal.tanh() } else { signal };
                self.x[layer][j] = val;
            }
        }
    }

    fn train(
        &mut self,
        inputs: &[f32],
        expected: &[f32],
        is_classification: bool,
        alpha: f32
    ) {
        self.propagate(inputs, is_classification);

        // output deltas
        for j in 1..=self.d[self.l] {
            let xlj = self.x[self.l][j];
            let target = if j - 1 < expected.len() { expected[j - 1] } else { 0.0 };
            let mut delta = xlj - target;
            if is_classification { delta *= 1.0 - xlj.powi(2); }
            self.deltas[self.l][j] = delta;
        }

        // hidden layers
        if self.l >= 1 {
            for layer in (2..=self.l).rev() {
                for i in 1..=self.d[layer - 1] {
                    let mut total = 0.0;
                    for j in 1..=self.d[layer] {
                        total += self.w[layer][i][j] * self.deltas[layer][j];
                    }
                    total *= 1.0 - self.x[layer - 1][i].powi(2);
                    self.deltas[layer - 1][i] = total;
                }
            }
        }

        // update weights
        for layer in 1..=self.l {
            for i in 0..=self.d[layer - 1] {
                for j in 1..=self.d[layer] {
                    self.w[layer][i][j] -= alpha * self.x[layer - 1][i] * self.deltas[layer][j];
                }
            }
        }
    }

    pub fn save(&self, filepath: &str) -> std::io::Result<()> {
        let mut file = File::create(filepath)?;
        
        // Save topology
        let d_str: Vec<String> = self.d.iter().map(|x| x.to_string()).collect();
        writeln!(file, "{}", d_str.join(" "))?;

        // Save weights
        for layer in 1..=self.l {
            for i in 0..=self.d[layer - 1] {
                let row_str: Vec<String> = self.w[layer][i].iter().map(|x| x.to_string()).collect();
                writeln!(file, "{}", row_str.join(" "))?;
            }
        }
        Ok(())
    }

    pub fn load(filepath: &str) -> std::io::Result<Self> {
        let file = File::open(filepath)?;
        let reader = BufReader::new(file);
        let mut lines = reader.lines();

        // Read topology
        let first_line = lines.next().ok_or(std::io::Error::new(std::io::ErrorKind::InvalidData, "Empty file"))??;
        let d: Vec<usize> = first_line.split_whitespace()
            .map(|s| s.parse().map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e)))
            .collect::<Result<_, _>>()?;

        let mut mlp = Self::new(d.clone());

        // Read weights
        for layer in 1..=mlp.l {
            for i in 0..=mlp.d[layer - 1] {
                let line = lines.next().ok_or(std::io::Error::new(std::io::ErrorKind::InvalidData, "Missing weights"))??;
                let weights: Vec<f32> = line.split_whitespace()
                    .map(|s| s.parse().map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e)))
                    .collect::<Result<_, _>>()?;
                
                mlp.w[layer][i] = weights;
            }
        }

        Ok(mlp)
    }
}

// --- FFI MLP ---

#[no_mangle]
pub extern "C" fn mlp_new(d: *const usize, len: usize) -> *mut MLP {
    let layers = unsafe { slice::from_raw_parts(d, len) };
    let mlp = MLP::new(layers.to_vec());
    Box::into_raw(Box::new(mlp))
}

#[no_mangle]
pub extern "C" fn mlp_predict(
    ptr: *mut MLP,
    inputs: *const f32,
    len_inputs: i32,
    is_classification: bool,
    outputs: *mut f32,
    len_outputs: i32
) {
    if ptr.is_null() || inputs.is_null() || outputs.is_null() { return; }
    let mlp = unsafe { &mut *ptr };
    let input_slice = unsafe { slice::from_raw_parts(inputs, len_inputs as usize) };
    let output_slice = unsafe { slice::from_raw_parts_mut(outputs, len_outputs as usize) };

    mlp.propagate(input_slice, is_classification);

    // Copy output from last layer to outputs buffer
    for i in 0..len_outputs as usize {
        if i + 1 < mlp.x[mlp.l].len() {
            output_slice[i] = mlp.x[mlp.l][i + 1];
        }
    }
}

#[no_mangle]
pub extern "C" fn mlp_train(
    ptr: *mut MLP,
    inputs: *const f32,
    len_inputs: i32,
    expected: *const f32,
    len_expected: i32,
    is_classification: bool,
    alpha: f32
) {
    if ptr.is_null() || inputs.is_null() || expected.is_null() { return; }
    let mlp = unsafe { &mut *ptr };
    let input_slice = unsafe { slice::from_raw_parts(inputs, len_inputs as usize) };
    let expected_slice = unsafe { slice::from_raw_parts(expected, len_expected as usize) };

    mlp.train(input_slice, expected_slice, is_classification, alpha);
}

#[no_mangle]
pub extern "C" fn mlp_free(ptr: *mut MLP) {
    if ptr.is_null() { return; }
    unsafe {
        let _ = Box::from_raw(ptr);
    }
}

#[no_mangle]
pub extern "C" fn mlp_save(ptr: *mut MLP, filepath: *const c_char) -> bool {
    if ptr.is_null() || filepath.is_null() { return false; }
    let mlp = unsafe { &*ptr };
    let c_str = unsafe { CStr::from_ptr(filepath) };
    let str_slice = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return false,
    };
    
    match mlp.save(str_slice) {
        Ok(_) => true,
        Err(_) => false,
    }
}

#[no_mangle]
pub extern "C" fn mlp_load(filepath: *const c_char) -> *mut MLP {
    if filepath.is_null() { return std::ptr::null_mut(); }
    let c_str = unsafe { CStr::from_ptr(filepath) };
    let str_slice = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };

    match MLP::load(str_slice) {
        Ok(mlp) => Box::into_raw(Box::new(mlp)),
        Err(_) => std::ptr::null_mut(),
    }
}
